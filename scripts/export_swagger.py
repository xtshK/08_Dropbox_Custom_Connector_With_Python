"""Export OpenAPI 3.0 spec from FastAPI and convert to Swagger 2.0 for Power Automate.

Usage:
    python scripts/export_swagger.py

The script:
1. Reads the OpenAPI 3.0 spec from the FastAPI app
2. Converts it to Swagger 2.0 format
3. Injects Power Automate x-ms-* extensions
4. Writes to swagger/dropbox-connector.swagger.json
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


def convert_openapi3_to_swagger2(spec: dict) -> dict:
    """Convert an OpenAPI 3.0 spec to Swagger 2.0 format."""
    swagger = {
        "swagger": "2.0",
        "info": spec.get("info", {}),
        "host": "localhost:8000",
        "basePath": "/",
        "schemes": ["https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "paths": {},
        "definitions": {},
        "securityDefinitions": {
            "apiKey": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header",
            }
        },
        "security": [{"apiKey": []}],
    }

    # Convert paths
    for path, methods in spec.get("paths", {}).items():
        swagger["paths"][path] = {}
        for method, operation in methods.items():
            if method in ("get", "post", "put", "delete", "patch"):
                swagger_op = _convert_operation(operation, spec)
                swagger["paths"][path][method] = swagger_op

    # Convert schemas from components to definitions
    components = spec.get("components", {})
    for name, schema in components.get("schemas", {}).items():
        swagger["definitions"][name] = _convert_schema(schema)

    return swagger


def _convert_operation(operation: dict, spec: dict) -> dict:
    result = {
        "operationId": operation.get("operationId", ""),
        "summary": operation.get("summary", ""),
        "description": operation.get("description", ""),
        "tags": operation.get("tags", []),
        "parameters": [],
        "responses": {},
    }

    # Convert parameters
    for param in operation.get("parameters", []):
        swagger_param = {
            "name": param.get("name"),
            "in": param.get("in"),
            "required": param.get("required", False),
            "type": "string",
        }
        schema = param.get("schema", {})
        if "type" in schema:
            swagger_param["type"] = schema["type"]
        if "description" in param:
            swagger_param["description"] = param["description"]
        if "default" in schema:
            swagger_param["default"] = schema["default"]
        result["parameters"].append(swagger_param)

    # Convert requestBody to parameter
    request_body = operation.get("requestBody", {})
    if request_body:
        content = request_body.get("content", {})
        # JSON body
        if "application/json" in content:
            json_schema = content["application/json"].get("schema", {})
            body_param = {
                "name": "body",
                "in": "body",
                "required": request_body.get("required", True),
                "schema": _resolve_ref(json_schema, "definitions"),
            }
            result["parameters"].append(body_param)
        # Multipart form
        elif "multipart/form-data" in content:
            result["consumes"] = ["multipart/form-data"]
            form_schema = content["multipart/form-data"].get("schema", {})
            properties = form_schema.get("properties", {})
            required_fields = form_schema.get("required", [])
            for prop_name, prop_schema in properties.items():
                param = {
                    "name": prop_name,
                    "in": "formData",
                    "required": prop_name in required_fields,
                    "description": prop_schema.get("description", ""),
                }
                if prop_schema.get("format") == "binary":
                    param["type"] = "file"
                else:
                    param["type"] = prop_schema.get("type", "string")
                    if "default" in prop_schema:
                        param["default"] = prop_schema["default"]
                result["parameters"].append(param)

    # Convert responses
    for code, response in operation.get("responses", {}).items():
        swagger_resp = {"description": response.get("description", "")}
        resp_content = response.get("content", {})
        if "application/json" in resp_content:
            schema = resp_content["application/json"].get("schema", {})
            swagger_resp["schema"] = _resolve_ref(schema, "definitions")
        result["responses"][code] = swagger_resp

    return result


def _resolve_ref(schema: dict, prefix: str = "definitions") -> dict:
    """Convert $ref from #/components/schemas/X to #/definitions/X."""
    if "$ref" in schema:
        ref = schema["$ref"].replace("#/components/schemas/", f"#/{prefix}/")
        return {"$ref": ref}
    if schema.get("type") == "array" and "items" in schema:
        return {"type": "array", "items": _resolve_ref(schema["items"], prefix)}
    return schema


def _convert_schema(schema: dict) -> dict:
    """Convert OpenAPI 3.0 schema to Swagger 2.0 schema."""
    result = {}
    for key, value in schema.items():
        if key == "anyOf":
            # Swagger 2.0 doesn't support anyOf; take the first non-null type
            for item in value:
                if item.get("type") != "null":
                    result.update(_convert_schema(item))
                    break
        elif key == "properties":
            result["properties"] = {}
            for pname, pschema in value.items():
                result["properties"][pname] = _convert_schema(pschema)
        elif key == "items":
            result["items"] = _convert_schema(value)
        elif key == "$ref":
            result["$ref"] = value.replace("#/components/schemas/", "#/definitions/")
        else:
            result[key] = value
    return result


def inject_power_automate_extensions(swagger: dict) -> dict:
    """Add Power Automate-specific x-ms-* extensions."""
    for path, methods in swagger.get("paths", {}).items():
        for method, operation in methods.items():
            # Add x-ms-trigger for polling trigger
            if operation.get("operationId") == "OnFileChanged":
                operation["x-ms-trigger"] = "poll"
                operation["x-ms-trigger-hint"] = "Monitors a Dropbox folder for file changes"
                # Hide cursor parameter
                for param in operation.get("parameters", []):
                    if param.get("name") == "cursor":
                        param["x-ms-visibility"] = "internal"

            # Add x-ms-summary to parameters
            for param in operation.get("parameters", []):
                if "x-ms-summary" not in param:
                    param["x-ms-summary"] = param.get("name", "").replace("_", " ").title()

    return swagger


def main():
    spec = app.openapi()

    swagger = convert_openapi3_to_swagger2(spec)
    swagger = inject_power_automate_extensions(swagger)

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "swagger")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "dropbox-connector.swagger.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(swagger, f, indent=2, ensure_ascii=False)

    print(f"Swagger 2.0 spec exported to: {output_path}")
    print(f"Operations: {sum(len(m) for m in swagger['paths'].values())}")


if __name__ == "__main__":
    main()
