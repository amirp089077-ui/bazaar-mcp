"""
Cafe Bazaar MCP Tool Definitions and Execution Handlers
Exposes 12 comprehensive tools conforming to the Model Context Protocol standard.
"""

import json
import logging
from typing import Any, Dict, List

from .analytics import appraise_app, compare_apps
from .client import BazaarClient

logger = logging.getLogger("bazaar_mcp.tools")

client = BazaarClient()

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "bazaar_search_apps",
        "description": "Search applications and games on Cafe Bazaar (کافه بازار) by query string with rating, install count, and thumbnails.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword or app name (e.g. 'divar', 'اسنپ', 'فیلم')"},
                "limit": {"type": "integer", "description": "Maximum number of apps to return (default: 20)", "default": 20},
            },
            "required": ["query"],
        },
    },
    {
        "name": "bazaar_get_app_details",
        "description": "Get complete metadata for an application on Cafe Bazaar, including description, version, ratings, screenshots, and direct download links.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "Application Android package ID (e.g. 'ir.divar', 'com.shatelland.namava.mobile')"},
            },
            "required": ["package_name"],
        },
    },
    {
        "name": "bazaar_get_download_link",
        "description": "Generate direct, high-speed CDN APK download links and checksum hashes for a Cafe Bazaar app.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "Application package name (e.g. 'ir.divar')"},
            },
            "required": ["package_name"],
        },
    },
    {
        "name": "bazaar_get_reviews",
        "description": "Extract real user reviews, ratings, and comments for an application on Cafe Bazaar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "Application package name (e.g. 'ir.divar')"},
                "limit": {"type": "integer", "description": "Maximum reviews to fetch (default: 25)", "default": 25},
            },
            "required": ["package_name"],
        },
    },
    {
        "name": "bazaar_list_categories",
        "description": "List all official application and game categories available on Cafe Bazaar with Persian and English labels.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "bazaar_get_category_apps",
        "description": "Retrieve popular applications in a specific category on Cafe Bazaar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category_slug": {"type": "string", "description": "Category slug or key (e.g. 'shopping', 'finance', 'video-audio', 'tools', 'action-games')"},
                "limit": {"type": "integer", "description": "Maximum apps to return (default: 20)", "default": 20},
            },
            "required": ["category_slug"],
        },
    },
    {
        "name": "bazaar_similar_apps",
        "description": "Find recommended, alternative, or similar applications on Cafe Bazaar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "Target application package name"},
                "limit": {"type": "integer", "description": "Maximum similar apps to return (default: 10)", "default": 10},
            },
            "required": ["package_name"],
        },
    },
    {
        "name": "bazaar_developer_apps",
        "description": "List all applications created and published by a specific developer or publisher.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "developer_query": {"type": "string", "description": "Developer name or publisher keyword (e.g. 'دیوار', 'کافه بازار', 'Shatel')"},
                "limit": {"type": "integer", "description": "Maximum apps to return (default: 20)", "default": 20},
            },
            "required": ["developer_query"],
        },
    },
    {
        "name": "bazaar_appraise_app",
        "description": "Perform an automated quality, popularity, and efficiency appraisal for a Cafe Bazaar application.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "Application package name to appraise"},
            },
            "required": ["package_name"],
        },
    },
    {
        "name": "bazaar_compare_apps",
        "description": "Compare two applications side-by-side on Cafe Bazaar based on rating, size, downloads, and popularity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name_1": {"type": "string", "description": "First app package name"},
                "package_name_2": {"type": "string", "description": "Second app package name"},
            },
            "required": ["package_name_1", "package_name_2"],
        },
    },
    {
        "name": "bazaar_status",
        "description": "Check the health and operational status of the Cafe Bazaar MCP server and connectivity to Bazaar API endpoints.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "bazaar_help",
        "description": "Provide a comprehensive guide and overview of all available tools in the Bazaar MCP server.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def execute_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Dispatch and execute an MCP tool invocation."""
    try:
        if name == "bazaar_search_apps":
            query = arguments.get("query", "")
            limit = int(arguments.get("limit", 20))
            return client.search_apps(query=query, limit=limit)

        elif name == "bazaar_get_app_details":
            pkg = arguments.get("package_name", "")
            return client.get_app_details(package_name=pkg)

        elif name == "bazaar_get_download_link":
            pkg = arguments.get("package_name", "")
            return client.get_download_info(package_name=pkg)

        elif name == "bazaar_get_reviews":
            pkg = arguments.get("package_name", "")
            limit = int(arguments.get("limit", 25))
            return client.get_reviews(package_name=pkg, limit=limit)

        elif name == "bazaar_list_categories":
            return client.list_categories()

        elif name == "bazaar_get_category_apps":
            cat = arguments.get("category_slug", "")
            limit = int(arguments.get("limit", 20))
            return client.get_category_apps(category_slug=cat, limit=limit)

        elif name == "bazaar_similar_apps":
            pkg = arguments.get("package_name", "")
            limit = int(arguments.get("limit", 10))
            return client.get_similar_apps(package_name=pkg, limit=limit)

        elif name == "bazaar_developer_apps":
            dev = arguments.get("developer_query", "")
            limit = int(arguments.get("limit", 20))
            return client.get_developer_apps(developer_query=dev, limit=limit)

        elif name == "bazaar_appraise_app":
            pkg = arguments.get("package_name", "")
            details = client.get_app_details(package_name=pkg)
            return appraise_app(details)

        elif name == "bazaar_compare_apps":
            pkg1 = arguments.get("package_name_1", "")
            pkg2 = arguments.get("package_name_2", "")
            d1 = client.get_app_details(pkg1)
            d2 = client.get_app_details(pkg2)
            return compare_apps(d1, d2)

        elif name == "bazaar_status":
            test_res = client.search_apps("divar", limit=1)
            is_alive = len(test_res) > 0
            return {
                "server": "bazaar-mcp",
                "version": "1.0.0",
                "status": "online" if is_alive else "degraded",
                "api_endpoint": "https://api.cafebazaar.ir/rest-v1/process",
                "web_endpoint": "https://cafebazaar.ir",
                "features": [
                    "search_apps",
                    "app_details",
                    "direct_apk_download",
                    "user_reviews",
                    "categories",
                    "similarity_engine",
                    "appraisal_and_comparison",
                ],
            }

        elif name == "bazaar_help":
            return {
                "description": "Cafe Bazaar MCP Server provides full access to Iranian apps and games store.",
                "tools_count": len(TOOLS),
                "available_tools": [
                    {"name": t["name"], "description": t["description"]} for t in TOOLS
                ],
            }

        else:
            return {"error": f"Tool '{name}' not found."}

    except Exception as ex:
        logger.exception("Error executing tool %s: %s", name, ex)
        return {"error": str(ex), "tool": name}
