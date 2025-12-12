from typing import Any, Optional, Dict
from fastapi import Response
from fastapi.responses import JSONResponse
import uuid


def create_response(
    success: bool = True,
    data: Any = None,
    error: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
    status_code: int = 200
) -> JSONResponse:
    """
    Create a standardized API response
    
    Args:
        success: Whether the operation was successful
        data: Response data
        error: Error information with code, message, and details
        trace_id: Unique trace ID for request tracking
        status_code: HTTP status code
    
    Returns:
        JSONResponse with standardized format
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    
    response_data = {
        "success": success,
        "data": data,
        "error": error or {},
        "trace_id": trace_id
    }
    
    return JSONResponse(content=response_data, status_code=status_code)


def success_response(
    data: Any = None,
    trace_id: Optional[str] = None,
    status_code: int = 200
) -> JSONResponse:
    """Create a success response"""
    return create_response(
        success=True,
        data=data,
        trace_id=trace_id,
        status_code=status_code
    )


def error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
    status_code: int = 400
) -> JSONResponse:
    """Create an error response"""
    error = {
        "code": code,
        "message": message,
        "details": details or {}
    }
    return create_response(
        success=False,
        error=error,
        trace_id=trace_id,
        status_code=status_code
    )

