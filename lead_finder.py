"""
lead_finder.py
--------------
Functions to find potential leads (companies / people) through
Google Search and Hunter.io. Keep API keys in .env, never hard-code them.

Note on LinkedIn: LinkedIn's Terms of Service prohibit automated scraping
of the site. There is no function here that scrapes LinkedIn directly.
If your task genuinely requires LinkedIn leads, use LinkedIn Sales
Navigator (official, paid) or an enrichment provider like Apollo.io or
Snov.io that has a proper licensed API - the pattern below (a function
that returns a list of dicts) is identical, you'd just swap the request.
"""

import requests


def search_google_leads(query: str, api_key: str, cse_id: str, num_results: int = 10) -> list[dict]:
    """
    Search Google (via Custom Search JSON API) for a query like
    '"marketing agency" contact email site:.com'.

    Returns a list of dicts: [{title, link, snippet}, ...]
    """
    url = "https://www.googleapis.com/customsearch/v1"
    results = []
    # Google's API returns max 10 per request, paginate with 'start'
    for start in range(1, num_results + 1, 10):
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "start": start,
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("items", []):
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
            })
        if len(results) >= num_results:
            break
    return results[:num_results]


def find_emails_for_domain(domain: str, api_key: str, limit: int = 10) -> list[dict]:
    """
    Use Hunter.io's Domain Search to find real, verified emails at a
    company domain (e.g. "example.com").

    Returns a list of dicts: [{first_name, last_name, position, email, confidence}, ...]
    """
    url = "https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": api_key,
        "limit": limit,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json().get("data", {})

    leads = []
    for person in data.get("emails", []):
        leads.append({
            "first_name": person.get("first_name"),
            "last_name": person.get("last_name"),
            "position": person.get("position"),
            "email": person.get("value"),
            "confidence": person.get("confidence"),
            "domain": domain,
        })
    return leads
