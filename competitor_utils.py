from urllib.parse import urlparse


def classify_competitor(url, title=""):
    """
    Enhanced competitor classification that filters out:
    - Wikipedia and encyclopedias
    - Forums (Reddit, Quora, etc.)
    - Social media
    - News/blog articles
    - Directories
    - YouTube/videos
    """
    url_lower = url.lower()
    title_lower = title.lower() if title else ""

    # Primary venue (Funlab properties)
    if "holeymoley" in url_lower or "archiebrothers" in url_lower or "funlab" in url_lower:
        return "Funlab"

    # ========== NON-BUSINESS FILTERS (Strict) ==========
    
    # Wikipedia and encyclopedias
    if any(x in url_lower for x in ["wikipedia.org", "wikia.com", "fandom.com", "britannica.com"]):
        return "Encyclopedia"
    
    # Forums and Q&A sites
    if any(x in url_lower for x in ["reddit.com", "quora.com", "stackexchange.com", "answers.com", "forum"]):
        return "Forum"
    
    # Social media platforms
    if any(x in url_lower for x in ["facebook.com", "instagram.com", "tiktok.com", "twitter.com", "linkedin.com", "pinterest.com"]):
        return "Social"
    
    # Video platforms
    if any(x in url_lower for x in ["youtube.com", "youtu.be", "vimeo.com", "dailymotion.com"]):
        return "Social"
    
    # Review/directory sites (not actual competitors)
    if any(x in url_lower for x in ["tripadvisor", "yelp", "zomato", "foursquare", "trustpilot", 
                                     "google.com/maps", "newzealand.com", "aucklandnz.com", 
                                     "booking.com", "expedia"]):
        return "Directory"
    
    # News and blog platforms
    if any(x in url_lower for x in ["medium.com", "wordpress.com", "blogger.com", "tumblr.com",
                                     "/blog/", "/news/", "/article/", "nzherald", "stuff.co.nz"]):
        return "Content"
    
    # E-commerce platforms (unless they ARE the business)
    if any(x in url_lower for x in ["amazon.", "ebay.", "trademe.co.nz", "etsy."]):
        return "Marketplace"
    
    # Government and education sites
    if any(x in url_lower for x in [".gov", ".edu", ".ac.nz"]):
        return "Institutional"

    # ========== BUSINESS VALIDATION ==========
    
    # Check if it looks like a real business website
    # Real businesses typically have:
    # - Their own domain (not subdomains of platforms)
    # - Business-related keywords in title
    # - Not generic listing pages
    
    # Filter out generic "best of" or "top 10" listicles
    if any(x in title_lower for x in ["top 10", "best", "guide to", "how to find", "vs", "comparison"]):
        return "Content"
    
    # At this point, it's likely a direct competitor
    return "Direct Competitor"


def get_domain(url):
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def build_full_serp_table(results):
    """Build table with all SERP results"""
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
    """Filter to show only direct competitors (real businesses)"""
    filtered = []
    direct_rank = 1

    for i, item in enumerate(results, start=1):
        comp_type = classify_competitor(item["link"], item.get("title", ""))

        # Only include actual competitors (not Wikipedia, forums, etc.)
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
    """Get top N external direct competitors (excluding primary venue)"""
    external = []

    for i, item in enumerate(results, start=1):
        comp_type = classify_competitor(item["link"], item.get("title", ""))

        # Only real competitors, not Funlab properties
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
    """Find the primary venue (Funlab) in results"""
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
