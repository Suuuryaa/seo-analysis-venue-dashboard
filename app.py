import streamlit as st
import pandas as pd
import plotly.express as px
import serp_utils

from seo_utils import *
from scoring import calculate_seo_score
from comparison_utils import compare_metric
from leaderboard_utils import analyze_venue
from summary_utils import get_executive_summary, generate_ai_executive_summary
from pagespeed_utils import get_pagespeed_data
from competitor_utils import (
    build_full_serp_table,
    filter_direct_competitors,
    get_top_n_external_direct_competitors,
    get_primary_result
)
from benchmark_utils import build_benchmark_summary
from insight_utils import generate_strategic_insights
from keyword_opportunity_utils import find_keyword_opportunities


def build_recommended_fixes(
    title_has_keyword,
    meta_has_keyword,
    h1_has_keyword,
    kc,
    title_len,
    meta_len,
    missing_alt_count,
    pagespeed_data
):
    fixes = []

    if not title_has_keyword:
        fixes.append({
            "Priority": "High",
            "Issue": "Target keyword missing from title",
            "Recommended Fix": "Add the target keyword naturally to the page title."
        })

    if not meta_has_keyword:
        fixes.append({
            "Priority": "High",
            "Issue": "Target keyword missing from meta description",
            "Recommended Fix": "Rewrite the meta description to include the target keyword and a stronger call to action."
        })

    if not h1_has_keyword:
        fixes.append({
            "Priority": "High",
            "Issue": "Target keyword missing from H1",
            "Recommended Fix": "Add the target keyword or a close variation into the main H1 heading."
        })

    if kc == 0:
        fixes.append({
            "Priority": "High",
            "Issue": "Exact keyword not present in page content",
            "Recommended Fix": "Use the target keyword naturally in the intro, headings, and body copy."
        })
    elif kc < 3:
        fixes.append({
            "Priority": "Medium",
            "Issue": "Low keyword usage",
            "Recommended Fix": "Increase keyword usage naturally across the page without stuffing."
        })

    if title_len < 30 or title_len > 60:
        fixes.append({
            "Priority": "Medium",
            "Issue": "Title length not ideal",
            "Recommended Fix": "Keep title length between 30 and 60 characters."
        })

    if meta_len < 120 or meta_len > 160:
        fixes.append({
            "Priority": "Medium",
            "Issue": "Meta description length not ideal",
            "Recommended Fix": "Keep meta description length between 120 and 160 characters."
        })

    if missing_alt_count > 0:
        fixes.append({
            "Priority": "Medium",
            "Issue": f"{missing_alt_count} images missing ALT text",
            "Recommended Fix": "Add descriptive ALT text to improve accessibility and image SEO."
        })

    if pagespeed_data:
        perf = pagespeed_data.get("performance_score")
        if perf is not None and perf < 0.7:
            fixes.append({
                "Priority": "High",
                "Issue": "Weak mobile performance",
                "Recommended Fix": "Improve load speed, reduce blocking resources, and optimize heavy media."
            })

        cls = pagespeed_data.get("cumulative_layout_shift")
        if cls and cls != "None":
            fixes.append({
                "Priority": "Medium",
                "Issue": "Layout stability may need improvement",
                "Recommended Fix": "Reduce layout shifts by reserving space for images, embeds, and dynamic elements."
            })

    if not fixes:
        fixes.append({
            "Priority": "Low",
            "Issue": "No major issues detected",
            "Recommended Fix": "Maintain current optimization and monitor competitors."
        })

    return fixes


st.set_page_config(page_title="Venue SEO Intelligence Dashboard", layout="wide")

st.title("Venue SEO Intelligence Dashboard")

url = st.text_input("Enter Primary Venue URL")
keyword = st.text_input("Enter Target Keyword")
compare_url = st.text_input("Enter Comparison Venue URL (optional)")
pagespeed_api_key = st.text_input("Enter Google PageSpeed API Key", type="password")
serp_key = st.text_input("Enter SERPER API Key", type="password")
gemini_api_key = st.text_input("Enter Gemini API Key", type="password")

st.subheader("Multi-Venue Leaderboard")
venue_urls_text = st.text_area(
    "Enter multiple venue URLs (one per line)",
    height=150
)

col_a, col_b = st.columns(2)

with col_a:
    analyze_clicked = st.button("Analyze")

with col_b:
    competitors_clicked = st.button("Find Competitors")

if analyze_clicked:
    if url and keyword:
        try:
            st.session_state.keyword = keyword
            st.session_state.url = url

            soup, raw_html = get_page_soup(url)

            title = get_title(soup)
            meta = get_meta_description(soup)
            h1 = get_h1_tags(soup)
            text = get_text_content(soup)

            wc = count_words(text)
            kc = count_keyword(text, keyword)
            kd = keyword_density(text, keyword)

            token_counts, partial_match_total = count_partial_keyword_matches(text, keyword)
            token_coverage = keyword_token_coverage(text, keyword)

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

            summary = get_executive_summary(
                score=score,
                keyword_count=kc,
                missing_alt_count=len(missing_alt),
                word_count=wc
            )

            pagespeed_data = None
            if pagespeed_api_key:
                try:
                    pagespeed_data = get_pagespeed_data(url, pagespeed_api_key, strategy="mobile")
                except Exception as ps_error:
                    st.warning(f"PageSpeed API error: {ps_error}")

            recommended_fixes = build_recommended_fixes(
                title_has_keyword=title_has_keyword,
                meta_has_keyword=meta_has_keyword,
                h1_has_keyword=h1_has_keyword,
                kc=kc,
                title_len=title_len,
                meta_len=meta_len,
                missing_alt_count=len(missing_alt),
                pagespeed_data=pagespeed_data
            )

            st.subheader("Executive Summary")
            st.write("**Overall Status:**", summary["Overall Status"])
            st.write("**Top Issue:**", summary["Top Issue"])
            st.write("**Strongest Area:**", summary["Strongest Area"])
            st.write("**Priority Action:**", summary["Priority Action"])

            st.subheader("SEO Overview")
            col1, col2, col3 = st.columns(3)
            col1.metric("SEO Score", f"{score}/100")
            col2.metric("Word Count", wc)
            col3.metric("Keyword Density", f"{kd}%")

            tab1, tab2, tab3 = st.tabs(
                ["Technical SEO", "Content Analysis", "Comparison"]
            )

            with tab1:
                st.subheader("Technical SEO")
                st.write("**Title:**", title)
                st.write("**Title Length:**", title_len)
                st.write("**Meta Description:**", meta)
                st.write("**Meta Description Length:**", meta_len)
                st.write("**H1 Tags:**", h1)
                st.write("**Internal Links:**", len(internal))
                st.write("**External Links:**", len(external))
                st.write("**Images Missing Alt:**", len(missing_alt))

                if pagespeed_data:
                    st.subheader("PageSpeed Insights (Mobile)")

                    ps_col1, ps_col2, ps_col3, ps_col4 = st.columns(4)

                    performance_score = pagespeed_data["performance_score"]
                    accessibility_score = pagespeed_data["accessibility_score"]
                    best_practices_score = pagespeed_data["best_practices_score"]
                    seo_score_api = pagespeed_data["seo_score"]

                    ps_col1.metric(
                        "Performance",
                        f"{int(performance_score * 100) if performance_score is not None else 'N/A'}"
                    )
                    ps_col2.metric(
                        "Accessibility",
                        f"{int(accessibility_score * 100) if accessibility_score is not None else 'N/A'}"
                    )
                    ps_col3.metric(
                        "Best Practices",
                        f"{int(best_practices_score * 100) if best_practices_score is not None else 'N/A'}"
                    )
                    ps_col4.metric(
                        "SEO (PageSpeed)",
                        f"{int(seo_score_api * 100) if seo_score_api is not None else 'N/A'}"
                    )

                    st.write("**First Contentful Paint:**", pagespeed_data["first_contentful_paint"])
                    st.write("**Largest Contentful Paint:**", pagespeed_data["largest_contentful_paint"])
                    st.write("**Speed Index:**", pagespeed_data["speed_index"])
                    st.write("**Total Blocking Time:**", pagespeed_data["total_blocking_time"])
                    st.write("**Cumulative Layout Shift:**", pagespeed_data["cumulative_layout_shift"])

            with tab2:
                st.subheader("Content Analysis")
                st.write("**Target Keyword:**", keyword)
                st.write("**Exact Keyword Count:**", kc)
                st.write("**Exact Keyword Density:**", f"{kd}%")
                st.write("**Partial Match Total:**", partial_match_total)
                st.write("**Keyword Token Coverage:**", f"{token_coverage}%")
                st.write("**Token Counts:**", token_counts)
                st.write("**Keyword in Title:**", "Yes" if title_has_keyword else "No")
                st.write("**Keyword in Meta Description:**", "Yes" if meta_has_keyword else "No")
                st.write("**Keyword in H1:**", "Yes" if h1_has_keyword else "No")
                st.write("**Word Count:**", wc)

                st.subheader("Auto-Recommended SEO Fixes")
                fixes_df = pd.DataFrame(recommended_fixes)
                st.dataframe(fixes_df, use_container_width=True)

                st.subheader("Recommendations")
                if recs:
                    for r in recs:
                        st.write("-", r)
                else:
                    st.success("No major SEO issues found.")

            with tab3:
                st.subheader("Comparison")

                if compare_url:
                    compare_soup, compare_raw_html = get_page_soup(compare_url)

                    compare_title = get_title(compare_soup)
                    compare_meta = get_meta_description(compare_soup)
                    compare_h1 = get_h1_tags(compare_soup)
                    compare_text = get_text_content(compare_soup)

                    compare_wc = count_words(compare_text)
                    compare_kc = count_keyword(compare_text, keyword)
                    compare_kd = keyword_density(compare_text, keyword)

                    compare_internal, compare_external = get_links(compare_soup, compare_url)
                    compare_missing_alt = get_images_missing_alt(compare_soup)

                    compare_title_has_keyword = keyword_in_title(compare_title, keyword)
                    compare_meta_has_keyword = keyword_in_meta(compare_meta, keyword)
                    compare_h1_has_keyword = keyword_in_h1(compare_h1, keyword)

                    compare_title_len = title_length(compare_title)
                    compare_meta_len = meta_description_length(compare_meta)

                    compare_score, compare_recs = calculate_seo_score(
                        compare_title,
                        compare_meta,
                        compare_h1,
                        compare_kc,
                        compare_wc,
                        len(compare_missing_alt),
                        compare_title_has_keyword,
                        compare_meta_has_keyword,
                        compare_h1_has_keyword,
                        compare_title_len,
                        compare_meta_len
                    )

                    st.write("### Score Comparison")
                    st.write("**Primary Venue Score:**", score)
                    st.write("**Comparison Venue Score:**", compare_score)
                    st.write("**Winner:**", compare_metric(score, compare_score))

                    data = {
                        "Metric": [
                            "SEO Score",
                            "Word Count",
                            "Keyword Count",
                            "Keyword Density",
                            "Keyword in Title",
                            "Keyword in Meta",
                            "Keyword in H1",
                            "Internal Links",
                            "External Links",
                            "Images Missing ALT"
                        ],
                        "Primary Venue": [
                            str(score),
                            str(wc),
                            str(kc),
                            str(kd),
                            "Yes" if title_has_keyword else "No",
                            "Yes" if meta_has_keyword else "No",
                            "Yes" if h1_has_keyword else "No",
                            str(len(internal)),
                            str(len(external)),
                            str(len(missing_alt))
                        ],
                        "Comparison Venue": [
                            str(compare_score),
                            str(compare_wc),
                            str(compare_kc),
                            str(compare_kd),
                            "Yes" if compare_title_has_keyword else "No",
                            "Yes" if compare_meta_has_keyword else "No",
                            "Yes" if compare_h1_has_keyword else "No",
                            str(len(compare_internal)),
                            str(len(compare_external)),
                            str(len(compare_missing_alt))
                        ]
                    }

                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)

                    chart_data = pd.DataFrame({
                        "Venue": ["Primary Venue", "Comparison Venue"],
                        "SEO Score": [score, compare_score]
                    })

                    fig = px.bar(
                        chart_data,
                        x="Venue",
                        y="SEO Score",
                        color="Venue",
                        text="SEO Score"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.info("Add a comparison venue URL to compare two venues.")

            if venue_urls_text.strip():
                st.subheader("Leaderboard Results")

                venue_urls = [
                    line.strip()
                    for line in venue_urls_text.split("\n")
                    if line.strip()
                ]

                leaderboard_rows = []

                for venue_url in venue_urls:
                    try:
                        result = analyze_venue(venue_url, keyword)
                        leaderboard_rows.append(result)
                    except Exception as venue_error:
                        leaderboard_rows.append({
                            "Venue Name": venue_url,
                            "URL": f"Error: {venue_error}",
                            "SEO Score": 0,
                            "Score Band": "Error",
                            "Word Count": 0,
                            "Keyword Count": 0,
                            "Keyword Density": 0,
                            "Internal Links": 0,
                            "External Links": 0,
                            "Images Missing ALT": 0
                        })

                leaderboard_df = pd.DataFrame(leaderboard_rows)
                leaderboard_df = leaderboard_df.sort_values(
                    by="SEO Score",
                    ascending=False
                ).reset_index(drop=True)

                leaderboard_df.index = leaderboard_df.index + 1
                leaderboard_df.index.name = "Rank"

                st.dataframe(leaderboard_df, use_container_width=True)

                csv = leaderboard_df.to_csv(index=True).encode("utf-8")
                st.download_button(
                    label="Download Leaderboard CSV",
                    data=csv,
                    file_name="venue_seo_leaderboard.csv",
                    mime="text/csv"
                )

                leaderboard_chart = px.bar(
                    leaderboard_df.reset_index(),
                    x="Venue Name",
                    y="SEO Score",
                    color="Score Band",
                    text="SEO Score"
                )

                st.plotly_chart(leaderboard_chart, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter both primary URL and keyword.")

if competitors_clicked:
    if not serp_key:
        st.error("Please enter your SERPER API key.")
    elif not keyword:
        st.error("Please enter a target keyword first.")
    else:
        try:
            st.session_state.keyword = keyword
            competitors = serp_utils.get_serp_results(st.session_state.keyword, serp_key)

            if competitors:
                st.subheader("Full Google SERP Results")

                full_serp_rows = build_full_serp_table(competitors)
                full_serp_df = pd.DataFrame(full_serp_rows)
                st.dataframe(full_serp_df, use_container_width=True)

                st.subheader("Direct Competitors Only")

                direct_competitors = filter_direct_competitors(competitors)

                if direct_competitors:
                    direct_df = pd.DataFrame(direct_competitors)
                    st.dataframe(direct_df, use_container_width=True)
                else:
                    st.info("No direct competitors detected.")

                st.subheader("Primary Venue + Top 3 Direct Competitors")

                primary_result = get_primary_result(competitors)
                top3_external = get_top_n_external_direct_competitors(competitors, n=3)

                benchmark_rows = []

                if primary_result:
                    try:
                        primary_analysis = analyze_venue(primary_result["Link"], keyword)
                        primary_analysis["SERP Rank"] = primary_result["SERP Rank"]
                        primary_analysis["Role"] = "Primary Venue"
                        benchmark_rows.append(primary_analysis)
                    except Exception:
                        benchmark_rows.append({
                            "Venue Name": primary_result["Title"],
                            "URL": primary_result["Link"],
                            "SEO Score": 0,
                            "Score Band": "Error",
                            "Word Count": 0,
                            "Keyword Count": 0,
                            "Keyword Density": 0,
                            "Internal Links": 0,
                            "External Links": 0,
                            "Images Missing ALT": 0,
                            "SERP Rank": primary_result["SERP Rank"],
                            "Role": "Primary Venue"
                        })

                for item in top3_external:
                    try:
                        result = analyze_venue(item["Link"], keyword)
                        result["SERP Rank"] = item["SERP Rank"]
                        result["Role"] = "Direct Competitor"
                        benchmark_rows.append(result)
                    except Exception:
                        benchmark_rows.append({
                            "Venue Name": item["Title"],
                            "URL": item["Link"],
                            "SEO Score": 0,
                            "Score Band": "Error",
                            "Word Count": 0,
                            "Keyword Count": 0,
                            "Keyword Density": 0,
                            "Internal Links": 0,
                            "External Links": 0,
                            "Images Missing ALT": 0,
                            "SERP Rank": item["SERP Rank"],
                            "Role": "Direct Competitor"
                        })

                if benchmark_rows:
                    benchmark_df = pd.DataFrame(benchmark_rows)
                    benchmark_df = benchmark_df.sort_values(by="SERP Rank").reset_index(drop=True)
                    st.dataframe(benchmark_df, use_container_width=True)

                    chart_df = benchmark_df[["Venue Name", "SEO Score", "Role"]].copy()

                    fig = px.bar(
                        chart_df,
                        x="Venue Name",
                        y="SEO Score",
                        color="Role",
                        text="SEO Score"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    primary_rows = [row for row in benchmark_rows if row.get("Role") == "Primary Venue"]

                    if primary_rows:
                        summary_data = build_benchmark_summary(primary_rows[0], benchmark_rows)

                        st.subheader("Benchmark Summary")

                        c1, c2, c3, c4 = st.columns(4)

                        c1.metric("Primary Venue Rank", f"#{summary_data['primary_rank']}")
                        c2.metric("Primary SEO Score", summary_data["primary_score"])
                        c3.metric("Top Competitor", summary_data["top_competitor"])
                        c4.metric("Biggest Gap", summary_data["gap"])

                        insights = generate_strategic_insights(
                            primary_row=primary_rows[0],
                            benchmark_rows=benchmark_rows,
                            keyword=keyword
                        )

                        st.subheader("Strategic Insights")
                        for insight in insights:
                            st.write("-", insight)

                        primary_name = primary_rows[0].get("Venue Name", "Primary Venue")
                        primary_rank = primary_rows[0].get("SERP Rank", "N/A")
                        primary_score = primary_rows[0].get("SEO Score", 0)
                        top_competitor = summary_data["top_competitor"]

                        primary_fixes = build_recommended_fixes(
                            title_has_keyword=False,
                            meta_has_keyword=False,
                            h1_has_keyword=False,
                            kc=primary_rows[0].get("Keyword Count", 0),
                            title_len=50,
                            meta_len=150,
                            missing_alt_count=primary_rows[0].get("Images Missing ALT", 0),
                            pagespeed_data=None
                        )

                        st.subheader("AI Executive Summary")
                        ai_summary = generate_ai_executive_summary(
                            gemini_api_key=gemini_api_key,
                            primary_name=primary_name,
                            keyword=keyword,
                            primary_rank=primary_rank,
                            primary_score=primary_score,
                            top_competitor=top_competitor,
                            strategic_insights=insights,
                            recommended_fixes=primary_fixes
                        )

                        if ai_summary:
                            st.write(ai_summary)
                        else:
                            st.info("Enter Gemini API key to generate AI summary.")

                        st.subheader("Keyword Opportunities")

                        primary_text = ""
                        try:
                            primary_soup, _ = get_page_soup(primary_rows[0]["URL"])
                            primary_text = get_text_content(primary_soup)
                        except Exception:
                            primary_text = ""

                        competitor_texts = []
                        for row in benchmark_rows:
                            if row.get("Role") == "Direct Competitor":
                                try:
                                    comp_soup, _ = get_page_soup(row["URL"])
                                    competitor_texts.append(get_text_content(comp_soup))
                                except Exception:
                                    pass

                        opportunities = find_keyword_opportunities(primary_text, competitor_texts)

                        if opportunities:
                            opp_df = pd.DataFrame(
                                opportunities,
                                columns=["Keyword Opportunity", "Competitor Frequency", "Type"]
                            )
                            st.dataframe(opp_df, use_container_width=True)
                        else:
                            st.write("No clear keyword opportunities found.")

                else:
                    st.info("No benchmark rows available.")

            else:
                st.warning("No competitor results found.")

        except Exception as e:
            st.error(f"Competitor search error: {e}")