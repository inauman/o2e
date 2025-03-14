"""
Validation utilities for request validation.
"""
import typing as t
from flask import Request
import jsonschema


def validate_request(request: Request, schema: dict) -> t.Tuple[bool, t.List[str]]:
    """
    Validate a request against a JSON schema.
    
    Args:
        request: The Flask request object
        schema: The JSON schema to validate against
        
    Returns:
        A tuple of (is_valid, errors)
    """
    # Get JSON data from request
    try:
        data = request.get_json()
    except Exception:
        return False, ["Invalid JSON in request body"]
    
    # Validate against schema
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(data))
    
    if errors:
        # Format errors
        error_messages = []
        for error in errors:
            # Get path to the error
            path = ".".join(str(p) for p in error.path) if error.path else "root"
            error_messages.append(f"{path}: {error.message}")
        
        return False, error_messages
    
    return True, [] 