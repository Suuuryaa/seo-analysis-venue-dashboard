from urllib.parse import urlparse


def classify_competitor(url, title=""):
    url_lower = url.lower()

    if "holeymoley" in url_lower or "archiebrothers" in url_lower or "funlab" in url_lower:
        return "Funlab"

    if any(x in url_lower for x in ["tripadvisor", "yelp", "newzealand.com", "aucklandnz.com"]):
        return "Directory"

    if any(x in url_lower for x in ["facebook", "instagram", "tiktok", "youtube"]):
        return "Social"

    if "reddit" in url_lower:
        return "Forum"

    if any(x in url_lower for x in ["blog", "news", "article", "guide"]):
        return "Content"

    return "Direct Competitor"


def get_domain(url):
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def build_full_serp_table(results):
    rows = []

    for i, item in enumerate(results, start=1):
        comp_type = classify_competitor(item["link"], item.get("title", ""))

        rows.append({
            "SERP Rank": i,
            "Title": item.get("title", ""),
            "Link": item.get("link", ""),
            "Type": comp_type,
            "Snippet": item.get("snippet", "")
        })

    return rows


def filter_direct_competitors(results):
    filtered = []
    direct_rank = 1

    for i, item in enumerate(results, start=1):
        comp_type = classify_competitor(item["link"], item.get("title", ""))

        if comp_type in ["Direct Competitor", "Funlab"]:
            filtered.append({
                "Direct Rank": direct_rank,
                "SERP Rank": i,
                "Title": item.get("title", ""),
                "Link": item.get("link", ""),
                "Type": comp_type,
                "Snippet": item.get("snippet", ""),
                "Domain": get_domain(item.get("link", ""))
            })
            direct_rank += 1

    return filtered


def get_top_n_external_direct_competitors(results, n=3):
    external = []

    for i, item in enumerate(results, start=1):
        comp_type = classify_competitor(item["link"], item.get("title", ""))

        if comp_type == "Direct Competitor":
            external.append({
                "SERP Rank": i,
                "Title": item.get("title", ""),
                "Link": item.get("link", ""),
                "Type": comp_type,
                "Snippet": item.get("snippet", ""),
                "Domain": get_domain(item.get("link", ""))
            })

    return external[:n]


def get_primary_result(results):
    for i, item in enumerate(results, start=1):
        comp_type = classify_competitor(item["link"], item.get("title", ""))
        if comp_type == "Funlab":
            return {
                "SERP Rank": i,
                "Title": item.get("title", ""),
                "Link": item.get("link", ""),
                "Type": comp_type,
                "Snippet": item.get("snippet", ""),
                "Domain": get_domain(item.get("link", ""))
            }

    return None