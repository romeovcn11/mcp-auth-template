# MCP Auth Template

A secure Model Context Protocol (MCP) server template with built-in Bearer token authentication. This template provides a foundation for building authenticated MCP servers that can be integrated with various MCP clients.

## What This Code Does

This project implements a custom MCP server with the following features:

- **FastMCP Integration**: Built on top of the FastMCP framework for high-performance MCP server implementation
- **Bearer Token Authentication**: Secure authentication using Bearer tokens for all protected endpoints
- **SSE Transport**: Server-Sent Events transport for real-time communication
- **Health Check Endpoints**: Kubernetes-ready health check endpoints for monitoring
- **Custom Route Support**: Extensible routing system for additional endpoints
- **Environment-based Configuration**: Secure configuration management using environment variables

### Key Components

- **CustomMCP Class**: Extends FastMCP with authentication middleware
- **BearerAuthMiddleware**: Protects specified routes with token-based authentication
- **Health Check**: `/healthz` endpoint for monitoring and health checks
- **SSE Endpoints**: 
  - `/custom-mcp/sse` - Client receives responses
  - `/custom-mcp/messages/` - Client sends messages

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Environment Configuration

Create a `.env` file in the project root directory with the following variables:

```bash
# Required: Authentication token for MCP server
MCP_SERVER_BEARER_TOKEN=your_secure_token_here

# Optional: Override default server settings
# MCP_SERVER_HOST=0.0.0.0
# MCP_SERVER_PORT=9090
```

### Environment Variables Explained

- **`MCP_SERVER_BEARER_TOKEN`** (Required): The Bearer token that clients must provide to authenticate with the server. This should be a secure, randomly generated token.
- **`MCP_SERVER_HOST`** (Optional): The host address to bind the server to. Defaults to `0.0.0.0` (all interfaces).
- **`MCP_SERVER_PORT`** (Optional): The port number for the server. Defaults to `9090`.

## Installation and starting the Server

1. Clone and navigate to the project directory:
   ```bash
   git clone https://github.com/romeovcn11/mcp-auth-template.git
   cd mcp-auth-template
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```
3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Ensure your `.env` file is configured with the required `MCP_SERVER_BEARER_TOKEN`
6. Run the server:
   ```bash
   python server.py
   ```

The server will start and listen on the configured host and port (default: `0.0.0.0:9090`).

## Testing the Server

### 1. Health Check (No Authentication Required)

Test the health check endpoint:

```bash
curl http://0.0.0.0:9090/healthz
```

Expected response:
```json
{"status": "ok"}
```

### 2. MCP Endpoints (Authentication Required)

Test the protected MCP endpoints with your Bearer token:

```bash
# Replace 'your_secure_token_here' with your actual token from .env
curl -H "Authorization: Bearer your_secure_token_here" \
     http://0.0.0.0:9090/custom-mcp/sse
```

### Adding New Tools

To add new MCP tools, extend the `CustomMCP` class:

```python
@custom_mcp.tool()
async def your_custom_tool(param: str) -> str:
    """Description of your tool."""
    # Your tool implementation here
    return f"Result: {param}"
```

### Common Issues

1. **"MCP_SERVER_BEARER_TOKEN not set" Error**
   - Ensure your `.env` file exists and contains the required token
   - Check that the file is in the project root directory

2. **Port Already in Use**
   - Change the port in your `.env` file or kill the process using the port
   - Use `lsof -i :9090` to find processes using the default port

3. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check your Python version (3.8+ required)
