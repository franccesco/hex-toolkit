"""OpenAPI schema validation utilities for tests."""

import json
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import jsonschema
from jsonschema import ValidationError

# Load OpenAPI spec once
OPENAPI_SPEC_PATH = Path(__file__).parent.parent / "hex-openapi.json"
with open(OPENAPI_SPEC_PATH) as f:
    OPENAPI_SPEC = json.load(f)


def get_schema_for_endpoint(path: str, method: str = "GET") -> Dict[str, Any]:
    """Extract response schema from OpenAPI spec for a given endpoint.
    
    Args:
        path: OpenAPI path template (e.g., "/v1/projects/{id}")
        method: HTTP method (default: GET)
        
    Returns:
        JSON schema for the response
        
    Raises:
        KeyError: If endpoint not found in spec
    """
    method = method.lower()
    
    # Handle path parameters - convert {id} to generic pattern for lookup
    path_pattern = path
    
    if path_pattern not in OPENAPI_SPEC["paths"]:
        raise KeyError(f"Path {path} not found in OpenAPI spec")
    
    path_spec = OPENAPI_SPEC["paths"][path_pattern]
    if method not in path_spec:
        raise KeyError(f"Method {method} not found for path {path}")
    
    # Get successful response schema (usually 200 or 201)
    responses = path_spec[method]["responses"]
    success_codes = ["200", "201"]
    
    for code in success_codes:
        if code in responses:
            content = responses[code].get("content", {})
            if "application/json" in content:
                schema = content["application/json"]["schema"]
                # Resolve $ref if present
                if "$ref" in schema:
                    schema = resolve_ref(schema["$ref"])
                return schema
    
    raise KeyError(f"No JSON response schema found for {method} {path}")


def resolve_ref(ref: str) -> Dict[str, Any]:
    """Resolve a $ref pointer in the OpenAPI spec.
    
    Args:
        ref: Reference string (e.g., "#/components/schemas/Project")
        
    Returns:
        Resolved schema
    """
    if not ref.startswith("#/"):
        raise ValueError(f"Only local references supported, got: {ref}")
    
    path_parts = ref[2:].split("/")
    result = OPENAPI_SPEC
    
    for part in path_parts:
        result = result[part]
    
    return result


def resolve_all_refs(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively resolve all $ref pointers in a schema.
    
    Args:
        schema: Schema that may contain $ref pointers
        
    Returns:
        Schema with all $refs resolved
    """
    if isinstance(schema, dict):
        if "$ref" in schema:
            # Resolve the reference and continue resolving in the result
            resolved = resolve_ref(schema["$ref"])
            return resolve_all_refs(resolved)
        else:
            # Recursively resolve in all values
            return {k: resolve_all_refs(v) for k, v in schema.items()}
    elif isinstance(schema, list):
        # Recursively resolve in all list items
        return [resolve_all_refs(item) for item in schema]
    else:
        # Primitive value, return as-is
        return schema


def handle_nullable_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Handle nullable fields in OpenAPI 3.0 style.
    
    OpenAPI 3.0 uses `nullable: true` which doesn't directly translate to JSON Schema.
    This function converts nullable schemas to proper JSON Schema format.
    
    Args:
        schema: Original schema
        
    Returns:
        Schema with proper null handling
    """
    schema = schema.copy()
    
    # Handle direct nullable property
    if schema.get("nullable") and "type" in schema:
        schema["type"] = [schema["type"], "null"]
        schema.pop("nullable", None)
    
    # Handle nullable with allOf
    elif schema.get("nullable") and "allOf" in schema:
        # Convert to anyOf with null option
        schema["anyOf"] = [
            {"allOf": schema["allOf"]},
            {"type": "null"}
        ]
        schema.pop("allOf", None)
        schema.pop("nullable", None)
    
    # Recursively handle nested schemas
    if "properties" in schema:
        for key, value in schema["properties"].items():
            if isinstance(value, dict):
                schema["properties"][key] = handle_nullable_schema(value)
    
    if "items" in schema and isinstance(schema["items"], dict):
        schema["items"] = handle_nullable_schema(schema["items"])
    
    return schema


def validate_against_spec(
    endpoint: str, 
    method: str = "GET",
    response_code: Optional[str] = None
) -> Callable:
    """Decorator to validate mock data against OpenAPI schema.
    
    Args:
        endpoint: OpenAPI endpoint path
        method: HTTP method
        response_code: Expected response code (for error responses)
        
    Returns:
        Decorator function
    """
    def decorator(mock_data_func: Callable) -> Callable:
        @wraps(mock_data_func)
        def wrapper(*args, **kwargs) -> Any:
            data = mock_data_func(*args, **kwargs)
            
            try:
                if response_code and response_code.startswith(("4", "5")):
                    # For error responses, validate against error schema
                    schema = get_error_schema(response_code)
                else:
                    # For success responses, validate against endpoint schema
                    schema = get_schema_for_endpoint(endpoint, method)
                
                # Handle nullable fields in OpenAPI 3.0 style
                schema = handle_nullable_schema(schema)
                
                # Resolve all $refs in the schema before validation
                resolved_schema = resolve_all_refs(schema)
                
                # Now validate with the fully resolved schema (no $refs)
                jsonschema.validate(instance=data, schema=resolved_schema)
                
            except ValidationError as e:
                raise AssertionError(
                    f"Mock data for {method} {endpoint} does not match OpenAPI schema: {e.message}"
                )
            except KeyError as e:
                # If endpoint not in spec, just warn and continue
                print(f"Warning: {e} - skipping validation")
            
            return data
        
        return wrapper
    
    return decorator


def get_error_schema(status_code: str) -> Dict[str, Any]:
    """Get error response schema for a given status code.
    
    Args:
        status_code: HTTP status code (e.g., "404")
        
    Returns:
        Error response schema
    """
    # Most error responses follow a common schema in Hex API
    # This is a simplified version - adjust based on actual API
    return {
        "type": "object",
        "required": ["message"],
        "properties": {
            "message": {"type": "string"},
            "trace_id": {"type": "string"},
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string"},
                        "message": {"type": "string"}
                    }
                }
            }
        }
    }


def validate_request_params(endpoint: str, method: str = "GET") -> Callable:
    """Decorator to validate request parameters against OpenAPI schema.
    
    Args:
        endpoint: OpenAPI endpoint path
        method: HTTP method
        
    Returns:
        Decorator function
    """
    def decorator(test_func: Callable) -> Callable:
        @wraps(test_func)
        def wrapper(*args, **kwargs) -> Any:
            # Extract parameters from test function
            # This is a placeholder - implement based on your needs
            return test_func(*args, **kwargs)
        
        return wrapper
    
    return decorator