# Cafe Bazaar MCP Server (کافه بازار)

[![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A high-performance Model Context Protocol (MCP) server for **Cafe Bazaar (کافه بازار)**, providing AI agents and IDEs (Gemini IDE, Claude Desktop, Antigravity) with native access to Android applications, games, direct CDN APK downloads, user reviews, search, categories, and appraisal engines.

## 🚀 Features

- **App Search (`bazaar_search_apps`)**: Real-time search with Persian and English support, install counters, ratings, and icons.
- **App Details (`bazaar_get_app_details`)**: Complete application metadata including descriptions, versions, screenshots, package size, and ratings.
- **Direct APK Download (`bazaar_get_download_link`)**: Resolves high-speed Bazaar and ArvanCloud CDN download URLs and SHA1 checksums.
- **User Reviews (`bazaar_get_reviews`)**: Extracts authentic user comments, ratings, and feedback.
- **Categories (`bazaar_list_categories`, `bazaar_get_category_apps`)**: Access top apps across curated categories (Shopping, Finance, Games, Tools, etc.).
- **Related Apps (`bazaar_similar_apps`)**: Recommends similar and competing applications.
- **Developer Catalog (`bazaar_developer_apps`)**: Discovers applications created by specific publishers.
- **Quality Appraisal (`bazaar_appraise_app`, `bazaar_compare_apps`)**: AI-driven quality scoring (0–100) and head-to-head comparison.
- **Health Check (`bazaar_status`)**: Real-time diagnostic tool for server connectivity.

## 📦 Installation

```bash
pip install -e .
```

## ⚙️ Configuration

### Antigravity / Gemini IDE (`~/.gemini/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "bazaar": {
      "command": "python",
      "args": ["-m", "bazaar_mcp.server"]
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "bazaar": {
      "command": "python",
      "args": ["-m", "bazaar_mcp.server"]
    }
  }
}
```

## 🌐 Cloudflare Edge Deployment
Live server running at:
`https://bazaar-mcp.alphanet-edge.workers.dev`
- SSE Endpoint: `https://bazaar-mcp.alphanet-edge.workers.dev/sse`
- MCP JSON-RPC: `https://bazaar-mcp.alphanet-edge.workers.dev/mcp`
- Health: `https://bazaar-mcp.alphanet-edge.workers.dev/health`

## 📄 License
MIT License.
