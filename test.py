import pyairbnb
import json

# Define search parameters
currency = "BRL"  # Currency for the search
check_in = "2025-11-10"  # Check-in date
check_out = "2025-11-21"  # Check-out date
ne_lat = -1.3742  # North-East latitude (Belém do Pará area)
ne_long = -48.4458  # North-East longitude
sw_lat = -1.5242  # South-West latitude
sw_long = -48.5458  # South-West longitude
zoom_value = 7  # Zoom level for the map
price_min = 1000
price_max = 100000
place_type = "" #or "Entire home/apt" or empty
amenities = []  # Example: Filter for listings with WiFi and Pool or leave empty
free_cancellation = False  # Filter for listings with free/flexible cancellation
language = "pt"
proxy_url = ""

# Search listings within specified coordinates and date range using keyword arguments
search_results = pyairbnb.search_all(
    check_in=check_in,
    check_out=check_out,
    ne_lat=ne_lat,
    ne_long=ne_long,
    sw_lat=sw_lat,
    sw_long=sw_long,
    zoom_value=zoom_value,
    price_min=price_min,
    price_max=price_max,
    place_type=place_type,
    amenities=amenities,
    free_cancellation=free_cancellation,
    currency=currency,
    language=language,
    proxy_url=proxy_url
)

# Save the search results as a JSON file
with open('batch2.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(search_results))  # Convert results to JSON and write to file