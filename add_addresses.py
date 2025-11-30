import json
import requests
import time
from typing import Dict, Any, Optional

def get_address_from_coordinates(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """
    Get address from coordinates using Nominatim (OpenStreetMap) API.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary with full API response or None if request fails
    """
    # Using Nominatim API (free, no API key required)
    url = "https://nominatim.openstreetmap.org/reverse"
    
    params = {
        'lat': latitude,
        'lon': longitude,
        'format': 'json',
        'addressdetails': 1,
        'accept-language': 'pt-BR'
    }
    
    headers = {
        'User-Agent': 'COP30-Hotels-Research/1.0'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Return the entire response as a dictionary
        return data
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching address for ({latitude}, {longitude}): {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def process_batch_file(input_file: str, output_file: str, delay: float = 1.0):
    """
    Process batch JSON file and add addresses to each room.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
        delay: Delay between API requests in seconds (to respect rate limits)
    """
    print(f"Reading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        rooms = json.load(f)
    
    total_rooms = len(rooms)
    print(f"Found {total_rooms} rooms to process")
    
    for idx, room in enumerate(rooms, 1):
        # Check if coordinates exist
        if 'coordinates' in room and room['coordinates']:
            coords = room['coordinates']
            
            # Note: The JSON has a typo "longitud" instead of "longitude"
            latitude = coords.get('latitude')
            longitude = coords.get('longitud') or coords.get('longitude')
            
            if latitude is not None and longitude is not None:
                print(f"Processing room {idx}/{total_rooms} - ID: {room.get('room_id')}...", end=' ')
                
                # Get address from API
                address_data = get_address_from_coordinates(latitude, longitude)
                
                if address_data:
                    room['address'] = address_data
                    print(f"✓ Address added")
                else:
                    room['address'] = {'error': 'Address lookup failed'}
                    print(f"✗ Failed")
                
                # Respect rate limits (Nominatim requires max 1 request per second)
                if idx < total_rooms:
                    time.sleep(delay)
            else:
                print(f"Room {idx}/{total_rooms} - ID: {room.get('room_id')} - Missing coordinates")
                room['address'] = {'error': 'Coordinates not available'}
        else:
            print(f"Room {idx}/{total_rooms} - ID: {room.get('room_id')} - No coordinates field")
            room['address'] = {'error': 'Coordinates not available'}
    
    print(f"\nSaving results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(rooms, f, ensure_ascii=False, indent=2)
    
    print("Done!")


def main():
    input_file = 'batch2.json'
    output_file = 'batch2_with_addresses.json'
    
    # Rate limit: 1 request per second for Nominatim
    # Increase if using a different API or with API key
    delay = 1.0
    
    process_batch_file(input_file, output_file, delay)


if __name__ == '__main__':
    main()
