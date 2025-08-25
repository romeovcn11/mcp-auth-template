import logging
import os

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("mcp-custom.server.main")


async def health_check(request: Request) -> JSONResponse:
    """Simple health check endpoint for Kubernetes probes."""
    logger.debug("Received health check request.")
    return JSONResponse({"status": "ok"})


class CustomMCP(FastMCP):
    """Custom FastMCP server class integration with tool filtering."""

    class _BearerAuthMiddleware(BaseHTTPMiddleware):
        def __init__(self, app, token: str, protected_prefixes: list[str]) -> None:  # type: ignore[no-untyped-def]
            super().__init__(app)
            self._expected_token = token
            self._protected_prefixes = [p.rstrip("/") for p in protected_prefixes if p]

        async def dispatch(self, request: Request, call_next):  # type: ignore[override]
            path = request.url.path.rstrip("/")
            if any(path.startswith(prefix) for prefix in self._protected_prefixes):
                auth_header = request.headers.get("Authorization", "")
                if not auth_header.startswith("Bearer "):
                    return JSONResponse({"detail": "Unauthorized"}, status_code=401)
                provided = auth_header.split(" ", 1)[1]
                if provided != self._expected_token:
                    return JSONResponse({"detail": "Unauthorized"}, status_code=401)
            return await call_next(request)

    def sse_app(self, mount_path: str = "/"):
        """Create the SSE ASGI app and attach bearer auth middleware if configured."""
        app = super().sse_app(mount_path)

        # Load expected token from environment; require auth
        token = os.getenv("MCP_SERVER_BEARER_TOKEN")
        if not token:
            logger.error("MCP_SERVER_BEARER_TOKEN not set. Server cannot start without authentication token.")
            raise ValueError("MCP_SERVER_BEARER_TOKEN environment variable is required. Please set it before starting the server.")
        
        # Determine protected routes
        protected = ['/']
        app.add_middleware(self._BearerAuthMiddleware, token=token, protected_prefixes=protected)
        logger.info(
            "Bearer auth middleware enabled for SSE endpoints: %s",
            ", ".join(p.rstrip("/") for p in protected),
        )

        return app


# Initialize the main MCP server using the custom class
custom_mcp = CustomMCP(
    name="Your custom MCP",
    host="0.0.0.0",
    port=9090,
    sse_path="/custom-mcp/sse",  # Client appel et recoit les reponses
    message_path="/custom-mcp/messages/"  # Client {Dust} envoie les messages
)

# Add the health check endpoint using the decorator
@custom_mcp.custom_route("/healthz", methods=["GET"], include_in_schema=False)
async def _health_check_route(request: Request) -> JSONResponse:
    return await health_check(request)

if __name__ == "__main__":
    custom_mcp.run(transport="sse")