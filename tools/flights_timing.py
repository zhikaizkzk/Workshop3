import json
import os

import httpx
import requests
from bs4 import BeautifulSoup, Tag
from utils import debug

def flights_timing() -> str:
    """
    Returns a few options of flights
    """


    try:
        # Add timeout back and debug
        # limit to singapore airline first
        api_key = ""
        if not api_key:
            raise ValueError("Missing API key for AviationStack")
        url = f"http://api.aviationstack.com/v1/flights?access_key={api_key}&airline_name={"Singapore Airlines"}"
        response = requests.get(url)
        data = response.json()
        response.raise_for_status()

    except Exception as e:
        # Log error for debugging
        debug(f"[ERROR] flights_timing() failed: {str(e)}")

        # Fallback to local file
        fallback_path = "dummydata/flight_timing.txt"
        print(os.getcwd())
        if os.path.exists(fallback_path):
            debug(f"[INFO] Using fallback data from {fallback_path}")
            try:
                with open(fallback_path, "r", encoding="utf-8") as f:
                    fallback_data = f.read().strip()
                    try:
                        parsed = json.loads(fallback_data)
                        return json.dumps(parsed, indent=2)
                    except json.JSONDecodeError:
                        return fallback_data
            except Exception as read_err:
                debug(f"[ERROR] Could not read fallback file: {str(read_err)}")
                return "No flight data available due to read failure."
        else:
            debug("[ERROR] No fallback data file found.")
            return "No flight data available. Both API and fallback failed."

    # Fallback news if RSS fetch fails
    return data

