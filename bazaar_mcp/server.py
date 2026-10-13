"""
Cafe Bazaar Model Context Protocol (MCP) Standard Server
Standard I/O JSON-RPC transport for Antigravity, Claude Desktop, and Gemini IDE.
"""

import io
import json
import logging
import sys
from typing import Any, Dict, Optional

from .tools import TOOLS, execute_tool

# Ensure UTF-8 streams on Windows to prevent charmap errors
if sys.platform == "win32":
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [bazaar-mcp] %(message)s",
)
logger = logging.getLogger("bazaar_mcp.server")


class BazaarMCPServer:
    """Production MCP Server for Cafe Bazaar."""

    def __init__(self):
        self.server_info = {
            "name": "bazaar-mcp",
            "version": "1.0.0",
        }

    def handle_request(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        msg_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if not method:
            return None

        # 1. Initialize
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                    },
                    "serverInfo": self.server_info,
                },
            }

        # 2. Initialized Notification
        elif method == "notifications/initialized":
            return None

        # 3. Ping
        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        # 4. Tools List
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOLS,
                },
            }

        # 5. Tools Call
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            try:
                res = execute_tool(tool_name, args)
                text_content = json.dumps(res, ensure_ascii=False, indent=2)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": text_content,
                            }
                        ],
                        "isError": False,
                    },
                }
            except Exception as e:
                logger.exception("Error executing tool %s: %s", tool_name, e)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error executing tool {tool_name}: {str(e)}",
                            }
                        ],
                        "isError": True,
                    },
                }

        else:
            if msg_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found",
                    },
                }
            return None

    def run(self):
        """Main stdio loop."""
        logger.info("Starting Cafe Bazaar MCP Server (stdio transport)...")
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue

                req = json.loads(line)
                resp = self.handle_request(req)
                if resp is not None:
                    out = json.dumps(resp, ensure_ascii=False)
                    sys.stdout.write(out + "\n")
                    sys.stdout.flush()

            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as ex:
                logger.exception("Error in main server loop: %s", ex)


def main():
    server = BazaarMCPServer()
    server.run()


if __name__ == "__main__":
    main()
