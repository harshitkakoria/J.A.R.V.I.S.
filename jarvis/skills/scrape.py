"""Web scraping - news, stocks."""
import requests
from bs4 import BeautifulSoup


def handle(query: str) -> str:
    """Handle scraping."""
    q = query.lower()
    
    if any(kw in q for kw in ["news", "headline", "latest"]):
        return get_news()
    
    if "gold" in q:
        return get_gold()
    
    if "stock" in q or "market" in q:
        return get_stock()
    
    return None


def get_news() -> str:
    """Get news headlines."""
    try:
        url = "https://www.bbc.com/news"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        headlines = []
        for h2 in soup.find_all('h2', limit=3):
            text = h2.get_text().strip()
            if text:
                headlines.append(text)
        
        if headlines:
            return "Headlines: " + "; ".join(headlines)
    except:
        pass
    
    return "Couldn't fetch news"


def get_gold() -> str:
    """Get gold price."""
    try:
        # Using alternative gold price API
        url = "https://api.metals.live/v1/spot/gold"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        
        price_usd = data[0]["price"]
        price_inr = price_usd * 83  # Approx USD to INR
        
        return f"Gold: ${price_usd:.2f}/oz (₹{price_inr:.0f}/10g approx)"
    except:
        return "Couldn't fetch gold price"


def get_stock() -> str:
    """Get stock info."""
    return "Stock tracking requires API key. Visit alphavantage.co for free key"
