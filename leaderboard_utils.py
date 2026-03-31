from seo_utils import (
    get_page_soup,
    get_title,
    get_meta_description,
    get_h1_tags,
    get_text_content,
    count_words,
    count_keyword,
    keyword_density,
    get_links,
    get_images_missing_alt,
    keyword_in_title,
    keyword_in_meta,
    keyword_in_h1,
    title_length,
    meta_description_length
)
from scoring import calculate_seo_score
from urllib.parse import urlparse


def get_venue_name(url, title):
    if title and title != "No title found":
        return title[:60]

    parsed = urlparse(url)
    return parsed.netloc


def get_score_band(score):
    if score >= 80:
        return "Strong"
    elif score >= 60:
        return "Moderate"
    else:
        return "Weak"


def analyze_venue(url, keyword):
    soup, raw_html = get_page_soup(url)

    title = get_title(soup)
    meta = get_meta_description(soup)
    h1 = get_h1_tags(soup)

    text = get_text_content(soup)

    wc = count_words(text)
    kc = count_keyword(text, keyword)
    kd = keyword_density(text, keyword)

    internal, external = get_links(soup, url)
    missing_alt = get_images_missing_alt(soup)

    title_has_keyword = keyword_in_title(title, keyword)
    meta_has_keyword = keyword_in_meta(meta, keyword)
    h1_has_keyword = keyword_in_h1(h1, keyword)

    title_len = title_length(title)
    meta_len = meta_description_length(meta)

    score, recs = calculate_seo_score(
        title,
        meta,
        h1,
        kc,
        wc,
        len(missing_alt),
        title_has_keyword,
        meta_has_keyword,
        h1_has_keyword,
        title_len,
        meta_len
    )

    return {
        "Venue Name": get_venue_name(url, title),
        "URL": url,
        "SEO Score": score,
        "Score Band": get_score_band(score),
        "Word Count": wc,
        "Keyword Count": kc,
        "Keyword Density": kd,
        "Internal Links": len(internal),
        "External Links": len(external),
        "Images Missing ALT": len(missing_alt)
    }