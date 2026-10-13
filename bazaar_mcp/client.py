"""
Cafe Bazaar API Client
Handles REST API interactions with api.cafebazaar.ir and cafebazaar.ir web store.
"""

import json
import logging
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger("bazaar_mcp.client")

BAZAAR_API_BASE = "https://api.cafebazaar.ir/rest-v1/process"
BAZAAR_WEB_BASE = "https://cafebazaar.ir"
DEFAULT_USER_AGENT = "Bazaar/2600000"

BAZAAR_CATEGORIES = [
    {"slug": "shopping", "fa_name": "خرید و سفارش آنلاین", "en_name": "Shopping", "query": "خرید"},
    {"slug": "finance", "fa_name": "امور مالی و بانکی", "en_name": "Finance", "query": "بانک"},
    {"slug": "communication", "fa_name": "پیام‌رسان‌ها و ارتباطات", "en_name": "Communication", "query": "پیام رسان"},
    {"slug": "video-audio", "fa_name": "فیلم، ویدیو و صوت", "en_name": "Video & Audio", "query": "فیلم و سریال"},
    {"slug": "transportation", "fa_name": "رفت و آمد و نقشه", "en_name": "Transportation & Maps", "query": "نقشه و مسیریاب"},
    {"slug": "tools", "fa_name": "ابزارها و کاربردی", "en_name": "Tools", "query": "ابزار کاربردی"},
    {"slug": "education", "fa_name": "آموزش و یادگیری", "en_name": "Education", "query": "آموزش"},
    {"slug": "entertainment", "fa_name": "سرگرمی", "en_name": "Entertainment", "query": "سرگرمی"},
    {"slug": "news-magazines", "fa_name": "اخبار و مجلات", "en_name": "News & Magazines", "query": "خبر"},
    {"slug": "books-references", "fa_name": "کتاب‌ها و مراجع", "en_name": "Books & References", "query": "کتابخوان"},
    {"slug": "sports", "fa_name": "ورزش و تندرستی", "en_name": "Sports & Fitness", "query": "ورزش"},
    {"slug": "medical-health", "fa_name": "پزشکی و سلامت", "en_name": "Medical & Health", "query": "پزشکی"},
    {"slug": "action-games", "fa_name": "بازی‌های اکشن", "en_name": "Action Games", "query": "بازی اکشن"},
    {"slug": "strategy-games", "fa_name": "بازی‌های استراتژی", "en_name": "Strategy Games", "query": "بازی استراتژی"},
    {"slug": "puzzle-games", "fa_name": "بازی‌های معمایی و فکری", "en_name": "Puzzle Games", "query": "بازی معمایی"},
    {"slug": "racing-games", "fa_name": "بازی‌های رانندگی و موتوری", "en_name": "Racing Games", "query": "بازی ماشین"},
]


class BazaarClient:
    """Production client for Cafe Bazaar Android API and Web App store."""

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/json",
        }

    def _get_default_properties(self) -> Dict[str, Any]:
        """Generate standard client device properties required by Bazaar API."""
        return {
            "language": 1,
            "clientID": "bazaar-client",
            "clientVersion": "26.0.0",
            "clientVersionCode": 2600000,
            "isKidsEnabled": False,
            "androidClientInfo": {
                "sdkVersion": 33,
                "cpu": "arm64-v8a",
                "dpi": 480,
                "width": 1080,
                "height": 2400,
                "manufacturer": "Samsung",
                "model": "SM-G998B",
                "device": "taroko",
                "hardware": "qcom",
                "product": "taroko",
                "locale": "fa_IR",
                "mcc": 432,
                "mnc": 35,
            },
        }

    def _post_api(self, endpoint: str, single_request_key: str, single_request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute JSON RPC request against api.cafebazaar.ir/rest-v1/process."""
        url = f"{BAZAAR_API_BASE}/{endpoint}"
        body = {
            "properties": self._get_default_properties(),
            "singleRequest": {
                single_request_key: single_request_payload,
            },
        }
        data_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=self.headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_text = resp.read().decode("utf-8", errors="replace")
                parsed = json.loads(resp_text)
                return parsed
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="replace") if hasattr(he, "read") else ""
            logger.error("Bazaar API error %s: %s", he.code, err_body)
            try:
                return json.loads(err_body)
            except Exception:
                return {"error": f"HTTP {he.code}", "details": err_body}
        except Exception as ex:
            logger.exception("Failed to call Bazaar API %s", endpoint)
            return {"error": str(ex)}

    def search_apps(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search applications and games on Cafe Bazaar."""
        if not query or not query.strip():
            return []

        clean_query = query.strip()
        res = self._post_api("SearchV2Request", "searchV2Request", {"query": clean_query})
        single_reply = res.get("singleReply") or {}
        search_reply = single_reply.get("searchV2Reply") or {}
        page = search_reply.get("page") or {}
        page_body = page.get("pageBodyInfo", {}).get("pageBody", {})
        rows = page_body.get("rows") or []

        apps: List[Dict[str, Any]] = []
        for r in rows:
            item_info = None
            is_ad = False

            if "detailedAppItem" in r:
                item_info = r["detailedAppItem"].get("info")
                is_ad = r["detailedAppItem"].get("isAd", False)
            elif "appItemWithCustomDetail" in r:
                item_info = r["appItemWithCustomDetail"].get("info")
                is_ad = r["appItemWithCustomDetail"].get("isAd", False)
            elif "appItem" in r:
                item_info = r["appItem"].get("info") or r["appItem"]
                is_ad = r.get("isAd", False)

            if not item_info or not item_info.get("packageName"):
                continue

            screenshots = []
            for s in item_info.get("screenshots") or []:
                if isinstance(s, dict) and s.get("fullSize"):
                    screenshots.append(s["fullSize"])
                elif isinstance(s, str):
                    screenshots.append(s)

            app = {
                "package_name": item_info.get("packageName"),
                "name": item_info.get("name"),
                "rate": item_info.get("rate", 0.0),
                "installs": f"{item_info.get('installCountVerbose', '')}{item_info.get('installCountVerboseLabel', '')}".strip(),
                "category": item_info.get("category", ""),
                "price_string": item_info.get("paymentInfo", {}).get("priceString", "رایگان"),
                "is_ad": is_ad,
                "icon": item_info.get("image", ""),
                "screenshots": screenshots,
                "version_code": item_info.get("versionCode", 0),
                "bazaar_url": f"{BAZAAR_WEB_BASE}/app/{item_info.get('packageName')}",
            }
            apps.append(app)
            if len(apps) >= limit:
                break

        return apps

    def get_download_info(self, package_name: str) -> Dict[str, Any]:
        """Fetch verified CDN download info and tokens for a package."""
        if not package_name:
            return {"error": "Missing package_name"}

        clean_pkg = package_name.strip()
        res = self._post_api("AppDownloadInfoRequest", "appDownloadInfoRequest", {
            "packageName": clean_pkg,
            "downloadStatus": 1,
        })

        single_reply = res.get("singleReply") or {}
        dl_reply = single_reply.get("appDownloadInfoReply")
        if not dl_reply:
            err_msg = res.get("properties", {}).get("errorMessage") or res.get("error") or "Download info not found"
            return {"error": err_msg, "package_name": clean_pkg}

        urls = dl_reply.get("fullPathUrls") or []
        primary_url = urls[0] if urls else ""
        backup_url = urls[1] if len(urls) > 1 else ""

        size_bytes = int(dl_reply.get("packageSize") or dl_reply.get("installationSize") or 0)
        size_mb = round(size_bytes / (1024 * 1024), 2) if size_bytes > 0 else 0.0

        return {
            "package_name": clean_pkg,
            "app_name": dl_reply.get("appName", clean_pkg),
            "version_code": dl_reply.get("versionCode", 0),
            "package_size_bytes": size_bytes,
            "package_size_mb": size_mb,
            "sha1_hash": dl_reply.get("hashCode", ""),
            "download_url": primary_url,
            "backup_download_url": backup_url,
            "all_download_urls": urls,
            "cdn_prefix": dl_reply.get("cdnPrefix", []),
            "multi_connection": dl_reply.get("multiConnectionDownload", True),
        }

    def get_reviews(self, package_name: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Fetch real user reviews and ratings for an application."""
        if not package_name:
            return []

        clean_pkg = package_name.strip()
        res = self._post_api("AppDetailsReviewRequest", "appDetailsReviewRequest", {
            "packageName": clean_pkg,
        })

        single_reply = res.get("singleReply") or {}
        review_reply = single_reply.get("appDetailsReviewReply") or {}
        raw_reviews = review_reply.get("reviews") or []

        parsed: List[Dict[str, Any]] = []
        for r in raw_reviews[:limit]:
            parsed.append({
                "id": r.get("id"),
                "user": r.get("user") or "کاربر بازار",
                "rate": r.get("rate", 5),
                "comment": r.get("comment", "").strip(),
                "date": r.get("date", ""),
                "likes": r.get("likes", 0),
                "total_votes": r.get("total", 0),
                "version_code": r.get("versionCode", 0),
                "avatar_url": r.get("avatarURL", ""),
            })

        return parsed

    def get_app_details(self, package_name: str) -> Dict[str, Any]:
        """
        Fetch full application metadata by marrying the web store JSON-LD schema
        with the native CDN download endpoint.
        """
        if not package_name:
            return {"error": "Missing package_name"}

        clean_pkg = package_name.strip()
        web_url = f"{BAZAAR_WEB_BASE}/app/{clean_pkg}"

        meta: Dict[str, Any] = {
            "package_name": clean_pkg,
            "name": clean_pkg,
            "description": "",
            "category": "",
            "version_name": "",
            "version_code": 0,
            "size_kb": 0,
            "size_mb": 0.0,
            "rating": 0.0,
            "rating_count": 0,
            "icon": "",
            "screenshots": [],
            "bazaar_url": web_url,
            "developer": "",
            "price_irr": 0,
            "modified_date": "",
            "download_url": "",
        }

        # 1. Fetch web page metadata (JSON-LD)
        try:
            req = urllib.request.Request(
                web_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept-Language": "fa,en;q=0.9",
                },
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                html = resp.read().decode("utf-8", errors="replace")

                # Extract JSON-LD script blocks
                ld_blocks = re.findall(r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>(.*?)</script>', html, re.DOTALL)
                for block in ld_blocks:
                    try:
                        data = json.loads(block)
                        if data.get("@type") == "SoftwareApplication":
                            meta["name"] = data.get("name") or meta["name"]
                            meta["description"] = data.get("description") or meta["description"]
                            meta["version_name"] = data.get("softwareVersion") or meta["version_name"]
                            meta["size_kb"] = data.get("fileSize") or meta["size_kb"]
                            if meta["size_kb"]:
                                meta["size_mb"] = round(meta["size_kb"] / 1024, 2)
                            meta["icon"] = data.get("image") or meta["icon"]
                            if data.get("screenshot"):
                                meta["screenshots"].append(data["screenshot"])
                            meta["modified_date"] = data.get("dateModified") or meta["modified_date"]
                            meta["category"] = data.get("applicationCategory") or meta["category"]

                            agg = data.get("aggregateRating") or {}
                            meta["rating"] = float(agg.get("ratingValue") or 0.0)
                            meta["rating_count"] = int(agg.get("ratingCount") or 0)

                            offers = data.get("offers") or {}
                            meta["price_irr"] = offers.get("price", 0)
                    except Exception:
                        pass
        except Exception as ex:
            logger.warning("Could not fetch web JSON-LD for %s: %s", clean_pkg, ex)

        # 2. Enrich with CDN download information
        dl_info = self.get_download_info(clean_pkg)
        if "error" not in dl_info:
            meta["download_url"] = dl_info.get("download_url", "")
            meta["backup_download_url"] = dl_info.get("backup_download_url", "")
            meta["version_code"] = dl_info.get("version_code", meta["version_code"])
            if dl_info.get("package_size_mb"):
                meta["size_mb"] = dl_info.get("package_size_mb")
            meta["sha1_hash"] = dl_info.get("sha1_hash", "")
            if not meta["name"] or meta["name"] == clean_pkg:
                meta["name"] = dl_info.get("app_name", clean_pkg)

        # 3. If screenshots or category missing, query search to backfill
        if not meta.get("screenshots") or not meta.get("category"):
            search_matches = self.search_apps(clean_pkg, limit=5)
            for sm in search_matches:
                if sm.get("package_name") == clean_pkg:
                    if not meta.get("category"):
                        meta["category"] = sm.get("category", "")
                    if sm.get("screenshots"):
                        for sc in sm["screenshots"]:
                            if sc not in meta["screenshots"]:
                                meta["screenshots"].append(sc)
                    if not meta.get("icon") and sm.get("icon"):
                        meta["icon"] = sm.get("icon")
                    if not meta.get("installs"):
                        meta["installs"] = sm.get("installs")
                    break

        return meta

    def list_categories(self) -> List[Dict[str, Any]]:
        """List curated application and game categories available on Bazaar."""
        return BAZAAR_CATEGORIES

    def get_category_apps(self, category_slug: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve top apps in a specific category."""
        target_cat = None
        for cat in BAZAAR_CATEGORIES:
            if cat["slug"].lower() == category_slug.lower() or cat["en_name"].lower() == category_slug.lower():
                target_cat = cat
                break

        query = target_cat["query"] if target_cat else category_slug
        return self.search_apps(query, limit=limit)

    def get_similar_apps(self, package_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find applications similar or complementary to the target app."""
        details = self.get_app_details(package_name)
        query = details.get("category") or details.get("name") or package_name
        # clean query
        query = re.sub(r"Application|برنامه|نرم‌افزار", "", query).strip()
        if not query:
            query = package_name.split(".")[-1]

        results = self.search_apps(query, limit=limit + 3)
        return [app for app in results if app.get("package_name") != package_name][:limit]

    def get_developer_apps(self, developer_query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Find applications published by a specific developer."""
        return self.search_apps(developer_query, limit=limit)
