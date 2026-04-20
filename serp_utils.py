import requests
import time

def get_serp_results(keyword, api_key, location_params=None, max_retries=3):
    """
    Fetch SERP results from SERPER API with optional geo-targeting.
    
    Args:
        keyword: Search keyword
        api_key: SERPER API key
        location_params: Optional dict with 'gl' and 'location' for geo-targeting
        max_retries: Maximum number of retry attempts
        
    Returns:
        List of search results
    """
    url = "https://google.serper.dev/search"
    
    # Base payload
    payload = {
        "q": keyword,
        "num": 10  # Top 10 results
    }
    
    # Add geo-targeting if provided
    if location_params:
        if 'gl' in location_params:
            payload['gl'] = location_params['gl']  # Country code
        if 'location' in location_params:
            payload['location'] = location_params['location']  # City, Country
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("organic", [])
            
            elif response.status_code == 429:
                # Rate limited - wait and retry
                wait_time = (attempt + 1) * 2
                time.sleep(wait_time)
                continue
            
            else:
                raise Exception(f"SERPER API error: {response.status_code} - {response.text}")
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise Exception("SERPER API timeout after multiple retries")
        
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                raise e
    
    raise Exception("Failed to fetch SERP results after all retries")


def progressive_competitor_search(url, keyword, api_key, filter_func, min_competitors=5):
    """
    Progressive geographic search expansion.
    
    Starts with city-specific search, expands to country-wide, then global
    until minimum number of direct competitors found.
    
    Args:
        url: Primary venue URL (for location detection)
        keyword: Search keyword
        api_key: SERPER API key
        filter_func: Function to filter direct competitors from results
        min_competitors: Minimum competitors needed (default: 5)
        
    Returns:
        Tuple of (all_results, direct_competitors, search_level_message)
    """
    from location_utils import get_location_from_url
    
    location = get_location_from_url(url) if url else None
    
    # Track search progression
    search_log = []
    all_results = []
    direct_competitors = []
    
    # LEVEL 1: City-specific search
    if location and location['city']:
        search_query = f"{keyword} {location['city']} {location['country_name']}"
        search_log.append(f"🔍 Searching: {search_query}")
        
        location_params = {
            'gl': location['serper_gl'],
            'location': location['serper_location']
        }
        
        all_results = get_serp_results(search_query, api_key, location_params)
        direct_competitors = filter_func(all_results)
        
        if len(direct_competitors) >= min_competitors:
            return all_results, direct_competitors, search_log, f"🌍 {location['city']}, {location['country_name']}"
        
        search_log.append(f"⚠️ Only {len(direct_competitors)} direct competitors found in {location['city']}")
    
    # LEVEL 2: Country-wide search
    if location:
        search_query = f"{keyword} {location['country_name']}"
        search_log.append(f"🔄 Expanding to: {location['country_name']}")
        
        location_params = {
            'gl': location['serper_gl']
        }
        
        all_results = get_serp_results(search_query, api_key, location_params)
        direct_competitors = filter_func(all_results)
        
        if len(direct_competitors) >= min_competitors:
            return all_results, direct_competitors, search_log, f"🌍 {location['country_name']} (country-wide)"
        
        search_log.append(f"⚠️ Only {len(direct_competitors)} direct competitors found in {location['country_name']}")
    
    # LEVEL 3: Global search
    search_log.append(f"🔄 Expanding globally: {keyword}")
    
    all_results = get_serp_results(keyword, api_key)
    direct_competitors = filter_func(all_results)
    
    return all_results, direct_competitors, search_log, f"🌍 Global results"
