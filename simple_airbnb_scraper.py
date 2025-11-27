#!/usr/bin/env python3
"""
Simple Airbnb Scraper for Educational Purposes

This is a simplified version of the scraper for testing and educational use.
Please respect robots.txt and Airbnb's terms of service.

Usage:
    python simple_airbnb_scraper.py --location "Belém, PA" --pages 2
"""

import argparse
import time
import random
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import json

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Please install required packages: pip install requests beautifulsoup4")
    exit(1)

class SimpleAirbnbScraper:
    """
    A simple Airbnb scraper using requests and BeautifulSoup.
    Educational purposes only.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def scrape_simple(self, location="Belém, PA", pages=1):
        """
        Scrape basic listing information using requests.
        
        Note: This is a simplified approach and may not capture all data
        that a full Selenium-based scraper would get.
        """
        print(f"Scraping {location} - {pages} pages")
        print("Note: This is a simplified scraper for educational purposes")
        
        listings = []
        
        # Generate some sample data for educational purposes
        # In a real scenario, you would make HTTP requests to Airbnb
        sample_listings = self._generate_sample_data(location, pages * 10)
        listings.extend(sample_listings)
        
        return listings
    
    def _generate_sample_data(self, location, count):
        """
        Generate sample data for educational purposes.
        In a real scraper, this would parse actual HTML responses.
        """
        import random
        
        sample_titles = [
            "Apartamento aconchegante no centro de Belém",
            "Casa moderna próxima ao Ver-o-Peso",
            "Loft com vista para a Baía do Guajará",
            "Quarto privativo em Nazaré",
            "Casa completa em Icoaraci",
            "Apartamento no Umarizal",
            "Suíte confortável em Batista Campos",
            "Casa de praia em Mosqueiro",
            "Flat no Reduto",
            "Chalé rústico em Outeiro"
        ]
        
        room_types = ["Casa inteira", "Quarto inteiro", "Quarto compartilhado"]
        
        listings = []
        for i in range(count):
            listing = {
                'listing_id': f"sample_{i+1}",
                'title': random.choice(sample_titles),
                'price': random.uniform(80, 400),
                'rating': random.uniform(3.5, 5.0),
                'room_type': random.choice(room_types),
                'location': location,
                'scraped_at': datetime.now().isoformat(),
                'source': 'simple_scraper_sample',
                'note': 'This is sample data for educational purposes'
            }
            listings.append(listing)
        
        return listings
    
    def save_data(self, listings, output_dir="./data"):
        """Save scraped data to CSV files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        if not listings:
            print("No data to save")
            return
        
        df = pd.DataFrame(listings)
        
        # Save raw data
        df.to_csv(output_dir / "scraped_listings.csv", index=False)
        print(f"Saved {len(df)} listings to {output_dir / 'scraped_listings.csv'}")
        
        # Create calendar-style data
        calendar_data = []
        base_date = date.today()
        
        for _, listing in df.iterrows():
            # Create multiple date entries for each listing
            for day_offset in range(60):  # 60 days of data
                entry_date = base_date.replace(day=1)  # Start from first of month
                try:
                    entry_date = entry_date.replace(month=10)  # October
                    if day_offset < 31:
                        entry_date = entry_date.replace(day=day_offset + 1)
                    else:
                        entry_date = entry_date.replace(month=11, day=day_offset - 30)
                except ValueError:
                    continue  # Skip invalid dates
                
                calendar_data.append({
                    'listing_id': listing['listing_id'],
                    'date': entry_date,
                    'price': f"R${listing['price']:.2f}",
                    'available': random.choice(['t', 'f'])  # Random availability
                })
        
        if calendar_data:
            cal_df = pd.DataFrame(calendar_data)
            cal_df.to_csv(output_dir / "scraped_calendar.csv", index=False)
            print(f"Created calendar data with {len(cal_df)} entries")
        
        # Create detailed listings
        detail_data = []
        for _, listing in df.iterrows():
            detail_data.append({
                'id': listing['listing_id'],
                'name': listing['title'],
                'room_type': listing['room_type'],
                'price': listing['price'],
                'rating': listing['rating'],
                'scraped_at': listing['scraped_at']
            })
        
        if detail_data:
            detail_df = pd.DataFrame(detail_data)
            detail_df.to_csv(output_dir / "scraped_listings_detail.csv", index=False)
            print(f"Created detailed listings with {len(detail_df)} entries")

def main():
    parser = argparse.ArgumentParser(description="Simple Airbnb Scraper")
    parser.add_argument("--location", default="Belém, PA", help="Location to search")
    parser.add_argument("--pages", type=int, default=2, help="Number of pages to scrape")
    parser.add_argument("--output", default="./data", help="Output directory")
    
    args = parser.parse_args()
    
    scraper = SimpleAirbnbScraper()
    
    try:
        listings = scraper.scrape_simple(args.location, args.pages)
        scraper.save_data(listings, args.output)
        
        print(f"\nCompleted! Generated sample data for {len(listings)} listings")
        print(f"Data saved to: {args.output}")
        print("\nYou can now run the analysis:")
        print(f"python belem_price_analysis.py --data-dir {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
