"""
Cafe Bazaar Analytics and Appraisal Engine
Provides intelligent scoring, popularity ranking, and side-by-side app comparison.
"""

from typing import Any, Dict


def appraise_app(app: Dict[str, Any]) -> Dict[str, Any]:
    """
    Appraise an application based on rating, rating count, file size,
    and market presence.
    """
    rating = float(app.get("rating") or app.get("rate") or 0.0)
    rating_count = int(app.get("rating_count") or 0)
    size_mb = float(app.get("size_mb") or 0.0)
    installs = str(app.get("installs") or "")

    # 1. Rating Score (out of 50)
    rating_score = (rating / 5.0) * 50.0

    # 2. Popularity Score (out of 30)
    popularity_score = 0.0
    if rating_count > 500000 or "M" in installs or "میلیون" in installs:
        popularity_score = 30.0
        popularity_tier = "Megahit (ابربرنامه)"
    elif rating_count > 50000 or "K" in installs or "هزار" in installs:
        popularity_score = 22.0
        popularity_tier = "Popular (بسیار پرطرفدار)"
    elif rating_count > 5000:
        popularity_score = 15.0
        popularity_tier = "Moderate (متوسط)"
    else:
        popularity_score = 8.0
        popularity_tier = "Emerging / Niche (نوظهور یا محدود)"

    # 3. Size Efficiency Score (out of 20)
    size_score = 20.0
    if size_mb > 150:
        size_score = 10.0
    elif size_mb > 80:
        size_score = 14.0
    elif size_mb > 40:
        size_score = 17.0

    total_score = round(min(100.0, rating_score + popularity_score + size_score), 1)

    if total_score >= 85:
        recommendation = "Must Have (به شدت پیشنهاد می‌شود)"
    elif total_score >= 70:
        recommendation = "Recommended (پیشنهاد خوب)"
    elif total_score >= 55:
        recommendation = "Average (معمولی)"
    else:
        recommendation = "Needs Improvement (نیازمند بررسی)"

    return {
        "package_name": app.get("package_name"),
        "name": app.get("name"),
        "total_score": total_score,
        "rating_score": round(rating_score, 1),
        "popularity_score": round(popularity_score, 1),
        "size_score": round(size_score, 1),
        "popularity_tier": popularity_tier,
        "recommendation": recommendation,
        "summary": f"{app.get('name')} با امتیاز کیفی {total_score}/100 در رده '{popularity_tier}' ارزیابی شد.",
    }


def compare_apps(app_a: Dict[str, Any], app_b: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two Bazaar apps side by side."""
    score_a = appraise_app(app_a)
    score_b = appraise_app(app_b)

    winner = app_a.get("name") if score_a["total_score"] >= score_b["total_score"] else app_b.get("name")

    return {
        "app_1": {
            "name": app_a.get("name"),
            "package_name": app_a.get("package_name"),
            "rating": app_a.get("rating") or app_a.get("rate"),
            "size_mb": app_a.get("size_mb"),
            "score": score_a["total_score"],
            "tier": score_a["popularity_tier"],
        },
        "app_2": {
            "name": app_b.get("name"),
            "package_name": app_b.get("package_name"),
            "rating": app_b.get("rating") or app_b.get("rate"),
            "size_mb": app_b.get("size_mb"),
            "score": score_b["total_score"],
            "tier": score_b["popularity_tier"],
        },
        "winner": winner,
        "verdict": f"بر اساس معیارهای کیفیت و رضایت کاربران، '{winner}' برتر شناخته می‌شود.",
    }
