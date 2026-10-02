"""
Health check endpoint handler.

GET /health
"""

from src.utils.responses import health_ok


def handle_health(event: dict, context: object) -> dict:
    """
    Handle GET /health requests.
    
    Returns a simple health status indicating the service is running.
    """
    return health_ok()