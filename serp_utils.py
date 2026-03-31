import requests


def get_serp_results(keyword, api_key):
    url = "https://google.serper.dev/search"

    payload = {
        "q": keyword,
        "num": 10
    }

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code != 200:
        return []

    data = response.json()

    results = []
    for item in data.get("organic", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results