def calculate_seo_score(
    title,
    meta_description,
    h1_tags,
    keyword_count,
    word_count,
    missing_alt_count,
    keyword_in_title_flag,
    keyword_in_meta_flag,
    keyword_in_h1_flag,
    title_len,
    meta_len
):
    score = 0
    recommendations = []

    if title != "No title found":
        score += 10
    else:
        recommendations.append("Missing page title")

    if meta_description != "No meta description found":
        score += 10
    else:
        recommendations.append("Missing meta description")

    if len(h1_tags) > 0:
        score += 10
    else:
        recommendations.append("Add at least one H1 heading")

    if keyword_count > 0:
        score += 10
    else:
        recommendations.append("Keyword not used in page content")

    if keyword_in_title_flag:
        score += 10
    else:
        recommendations.append("Add target keyword to page title")

    if keyword_in_meta_flag:
        score += 10
    else:
        recommendations.append("Add target keyword to meta description")

    if keyword_in_h1_flag:
        score += 10
    else:
        recommendations.append("Add target keyword to H1 heading")

    if word_count >= 300:
        score += 10
    else:
        recommendations.append("Increase content depth to at least 300 words")

    if 30 <= title_len <= 60:
        score += 10
    else:
        recommendations.append("Keep title length between 30 and 60 characters")

    if 120 <= meta_len <= 160:
        score += 10
    else:
        recommendations.append("Keep meta description length between 120 and 160 characters")

    if missing_alt_count > 0:
        recommendations.append("Some images are missing ALT text")

    return score, recommendations