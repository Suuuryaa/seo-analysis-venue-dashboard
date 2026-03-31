import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re


def get_page_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml"), response.text


def get_title(soup):
    if soup.title:
        return soup.title.get_text(strip=True)
    return "No title found"


def get_meta_description(soup):
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        return meta_tag["content"].strip()
    return "No meta description found"


def get_h1_tags(soup):
    return [tag.get_text(strip=True) for tag in soup.find_all("h1")]


def get_text_content(soup):
    return soup.get_text(separator=" ", strip=True)


def count_words(text):
    return len(text.split())


def count_keyword(text, keyword):
    return text.lower().count(keyword.lower())


def keyword_density(text, keyword):
    total_words = count_words(text)
    if total_words == 0:
        return 0
    keyword_count = count_keyword(text, keyword)
    return round((keyword_count / total_words) * 100, 2)


def get_links(soup, base_url):
    internal_links = []
    external_links = []
    domain = urlparse(base_url).netloc

    for tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, tag["href"])
        parsed_url = urlparse(full_url)

        if parsed_url.netloc == domain:
            internal_links.append(full_url)
        else:
            external_links.append(full_url)

    return list(set(internal_links)), list(set(external_links))


def get_images_missing_alt(soup):
    missing_alt = []

    for img in soup.find_all("img"):
        if not img.get("alt"):
            missing_alt.append(img.get("src", "No src"))

    return missing_alt


def keyword_in_title(title, keyword):
    return keyword.lower() in title.lower()


def keyword_in_meta(meta_description, keyword):
    return keyword.lower() in meta_description.lower()


def keyword_in_h1(h1_tags, keyword):
    for h1 in h1_tags:
        if keyword.lower() in h1.lower():
            return True
    return False


def title_length(title):
    return len(title)


def meta_description_length(meta_description):
    return len(meta_description)


def get_keyword_tokens(keyword):
    return [token.strip().lower() for token in keyword.split() if token.strip()]


def count_partial_keyword_matches(text, keyword):
    text_lower = text.lower()
    tokens = get_keyword_tokens(keyword)

    token_counts = {}
    total_partial_matches = 0

    for token in tokens:
        matches = len(re.findall(rf"\b{re.escape(token)}\b", text_lower))
        token_counts[token] = matches
        total_partial_matches += matches

    return token_counts, total_partial_matches


def keyword_token_coverage(text, keyword):
    text_lower = text.lower()
    tokens = get_keyword_tokens(keyword)

    present_tokens = 0
    for token in tokens:
        if re.search(rf"\b{re.escape(token)}\b", text_lower):
            present_tokens += 1

    if len(tokens) == 0:
        return 0

    return round((present_tokens / len(tokens)) * 100, 2)