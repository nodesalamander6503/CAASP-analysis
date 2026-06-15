import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from pathlib import Path
from geopy.exc import GeocoderTimedOut, GeocoderRateLimited
import time
import random
time_till_wait = 3
wait_time = 7
wait_dur = 4
random_wait_chance = 1/21
random_wait_dur = 13
def getAddress(address_str, max_retries=16):
    """Returns (lat, lon) with OSM-compliant rate limiting and robust error handling."""
    # Clean input to prevent timeouts from malformed strings
    clean_addr = " ".join(address_str.strip().split()) + ", California"
    
    geolocator = Nominatim(
        user_agent="CA_school_mapper_contact@uni.edu",  # Required by OSM policy
        timeout=30  # Generous timeout for slow responses
    )
    
    for attempt in range(max_retries):
        try:
            # Dynamic delay: base 1.5s + exponential backoff + jitter
            delay = 1.5 + (2 ** attempt) + (random.random() * 3)
            print(f"Attempt {attempt+1}: Waiting {delay:.2f}s...")
            time.sleep(delay)
            
            location = geolocator.geocode(clean_addr)
            if location:
                return (location.latitude, location.longitude)
                
        except (GeocoderTimedOut, GeocoderRateLimited) as e:
            print(f"Retry {attempt+1}: {type(e).__name__}")
            continue
            
    return (None, None)  # All retries exhausted
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
}
class OwOException(Exception):
    def __init__(self, x):
        super().__init__("OwO - " + x)
class OwORequestException(OwOException):
    def __init__(self):
        super().__init__("Request error")
