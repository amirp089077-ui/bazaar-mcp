"""
Automated Unit and Integration Test Suite for Cafe Bazaar MCP Server
"""

import sys
import unittest

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from bazaar_mcp.analytics import appraise_app, compare_apps
from bazaar_mcp.client import BazaarClient
from bazaar_mcp.tools import TOOLS, execute_tool


class TestBazaarMCP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = BazaarClient()
        cls.test_package = "ir.divar"

    def test_01_tool_registration(self):
        self.assertGreaterEqual(len(TOOLS), 12)
        tool_names = [t["name"] for t in TOOLS]
        self.assertIn("bazaar_search_apps", tool_names)
        self.assertIn("bazaar_get_app_details", tool_names)
        self.assertIn("bazaar_get_download_link", tool_names)
        self.assertIn("bazaar_get_reviews", tool_names)
        self.assertIn("bazaar_status", tool_names)

    def test_02_search_apps(self):
        res = execute_tool("bazaar_search_apps", {"query": "divar", "limit": 5})
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        first = res[0]
        self.assertIn("package_name", first)
        self.assertIn("name", first)

    def test_03_get_app_details(self):
        res = execute_tool("bazaar_get_app_details", {"package_name": self.test_package})
        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("package_name"), self.test_package)
        self.assertTrue(res.get("name"))
        self.assertTrue(res.get("download_url"))

    def test_04_get_download_link(self):
        res = execute_tool("bazaar_get_download_link", {"package_name": self.test_package})
        self.assertIsInstance(res, dict)
        self.assertTrue(res.get("download_url"))
        self.assertTrue(res["download_url"].startswith("http"))
        self.assertGreater(res.get("package_size_bytes", 0), 1000000)

    def test_05_get_reviews(self):
        res = execute_tool("bazaar_get_reviews", {"package_name": self.test_package, "limit": 5})
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        first = res[0]
        self.assertIn("comment", first)
        self.assertIn("rate", first)

    def test_06_list_categories(self):
        res = execute_tool("bazaar_list_categories", {})
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 5)
        self.assertTrue(any(c["slug"] == "shopping" for c in res))

    def test_07_get_category_apps(self):
        res = execute_tool("bazaar_get_category_apps", {"category_slug": "shopping", "limit": 5})
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)

    def test_08_similar_apps(self):
        res = execute_tool("bazaar_similar_apps", {"package_name": self.test_package, "limit": 5})
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        self.assertFalse(any(a["package_name"] == self.test_package for a in res))

    def test_09_developer_apps(self):
        res = execute_tool("bazaar_developer_apps", {"developer_query": "دیوار", "limit": 5})
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)

    def test_10_appraise_app(self):
        res = execute_tool("bazaar_appraise_app", {"package_name": self.test_package})
        self.assertIsInstance(res, dict)
        self.assertIn("total_score", res)
        self.assertGreater(res["total_score"], 0)
        self.assertIn("popularity_tier", res)

    def test_11_compare_apps(self):
        res = execute_tool("bazaar_compare_apps", {
            "package_name_1": "ir.divar",
            "package_name_2": "com.shatelland.namava.mobile",
        })
        self.assertIsInstance(res, dict)
        self.assertIn("winner", res)
        self.assertIn("verdict", res)

    def test_12_status_and_help(self):
        st = execute_tool("bazaar_status", {})
        self.assertEqual(st.get("status"), "online")
        hp = execute_tool("bazaar_help", {})
        self.assertGreaterEqual(hp.get("tools_count", 0), 12)


if __name__ == "__main__":
    unittest.main()
