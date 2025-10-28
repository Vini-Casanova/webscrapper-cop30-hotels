#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import time
import random
import json
from urllib.parse import quote, urlencode
import re
import pyairbnb
import json

# Web scraping imports
try:
    import requests
    from bs4 import BeautifulSoup
    import selenium
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

def to_float_price(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    # Remove R$, $, thousand separators and spaces
    s = s.replace("R$", "").replace("$", "").replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None

def infer_default_window(today=None):
    today = today or date.today()
    year = today.year
    start = date(year, 10, 1)
    end = date(year, 11, 30)
    return start.isoformat(), end.isoformat()

class AirbnbScraper:
    """
    Educational web scraper for Airbnb listings.
    
    IMPORTANT: This is for educational purposes only. Please respect robots.txt
    and Airbnb's terms of service. Consider using official APIs when available.
    """
    
    def __init__(self, headless=True, delay_range=(2, 5)):
        self.headless = headless
        self.delay_range = delay_range
        self.driver = None
        self.session = requests.Session()
        
        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def init_selenium_driver(self):
        """Initialize Selenium WebDriver for dynamic content"""
        if not SCRAPING_AVAILABLE:
            raise ImportError("Selenium not available. Install with: pip install selenium beautifulsoup4 requests")
            
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            print("Make sure chromedriver is installed and in PATH")
            return False
    
    def random_delay(self):
        """Add random delay to avoid being blocked"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def scrape_search_results(self, location, checkin, checkout, adults=1, max_pages=5):
        """
        Scrape Airbnb search results for a given location and date range.
        
        Args:
            location (str): Location to search (e.g., "Belém, PA")
            checkin (str): Check-in date (YYYY-MM-DD)
            checkout (str): Check-out date (YYYY-MM-DD)
            adults (int): Number of adults
            max_pages (int): Maximum number of pages to scrape
            
        Returns:
            list: List of listing dictionaries
        """
        print(f"Starting scrape for {location} from {checkin} to {checkout}")
        
        if not self.init_selenium_driver():
            return []
        
        listings = []
        
        try:
            # Build search URL
            base_url = "https://www.airbnb.com/s/"
            params = {
                'query': location,
                'checkin': checkin,
                'checkout': checkout,
                'adults': adults,
                'source': 'structured_search_input_header',
                'search_type': 'autocomplete_click'
            }
            
            search_url = f"{base_url}?{urlencode(params)}"
            print(f"Searching URL: {search_url}")
            
            for page in range(max_pages):
                print(f"Scraping page {page + 1}/{max_pages}")
                
                if page > 0:
                    # Add page offset for subsequent pages
                    page_params = params.copy()
                    page_params['items_offset'] = page * 20
                    search_url = f"{base_url}?{urlencode(page_params)}"
                
                self.driver.get(search_url)
                self.random_delay()
                
                # Wait for listings to load
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="listing-card-title"]'))
                    )
                except TimeoutException:
                    print(f"Timeout waiting for listings on page {page + 1}")
                    continue
                
                # Extract listing data
                page_listings = self.extract_listing_data()
                listings.extend(page_listings)
                
                print(f"Found {len(page_listings)} listings on page {page + 1}")
                
                # Check if there's a next page
                if not self.has_next_page():
                    print("No more pages available")
                    break
                
                self.random_delay()
                
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
        
        print(f"Total listings scraped: {len(listings)}")
        return listings
    
    def extract_listing_data(self):
        """Extract listing data from current page"""
        listings = []
        
        try:
            # Find all listing cards
            listing_cards = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="listing-card-title"]')
            
            for i, card in enumerate(listing_cards):
                try:
                    listing_data = {}
                    
                    # Get the parent container
                    parent = card.find_element(By.XPATH, './ancestor::div[contains(@class, "listing")]')
                    
                    # Extract title
                    listing_data['title'] = card.text.strip()
                    
                    # Extract price
                    try:
                        price_element = parent.find_element(By.CSS_SELECTOR, '[data-testid="price-availability"]')
                        price_text = price_element.text
                        price_match = re.search(r'R\$\s*(\d+(?:[.,]\d+)*)', price_text)
                        if price_match:
                            price_str = price_match.group(1).replace('.', '').replace(',', '.')
                            listing_data['price'] = float(price_str)
                        else:
                            listing_data['price'] = None
                    except:
                        listing_data['price'] = None
                    
                    # Extract rating
                    try:
                        rating_element = parent.find_element(By.CSS_SELECTOR, '[data-testid="listing-card-subtitle"]')
                        rating_text = rating_element.text
                        rating_match = re.search(r'(\d+[.,]\d+)', rating_text)
                        if rating_match:
                            listing_data['rating'] = float(rating_match.group(1).replace(',', '.'))
                        else:
                            listing_data['rating'] = None
                    except:
                        listing_data['rating'] = None
                    
                    # Extract room type and details
                    try:
                        subtitle_element = parent.find_element(By.CSS_SELECTOR, '[data-testid="listing-card-subtitle"]')
                        listing_data['room_type'] = subtitle_element.text.split('·')[0].strip()
                    except:
                        listing_data['room_type'] = None
                    
                    # Extract listing ID from URL if possible
                    try:
                        link_element = parent.find_element(By.CSS_SELECTOR, 'a[href*="/rooms/"]')
                        href = link_element.get_attribute('href')
                        id_match = re.search(r'/rooms/(\d+)', href)
                        if id_match:
                            listing_data['listing_id'] = int(id_match.group(1))
                        else:
                            listing_data['listing_id'] = f"scraped_{int(time.time())}_{i}"
                    except:
                        listing_data['listing_id'] = f"scraped_{int(time.time())}_{i}"
                    
                    # Add scrape metadata
                    listing_data['scraped_at'] = datetime.now().isoformat()
                    listing_data['source'] = 'airbnb_scraper'
                    
                    if listing_data['title']:  # Only add if we got at least the title
                        listings.append(listing_data)
                        
                except Exception as e:
                    print(f"Error extracting listing {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error finding listing cards: {e}")
            
        return listings
    
    def has_next_page(self):
        """Check if there's a next page button"""
        try:
            next_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label*="Next"]')
            return len(next_buttons) > 0 and next_buttons[0].is_enabled()
        except:
            return False
    
    def save_scraped_data(self, listings, data_dir):
        """Save scraped data to CSV files"""
        if not listings:
            print("No listings to save")
            return
        
        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to DataFrame
        df = pd.DataFrame(listings)
        
        # Save raw scraped data
        df.to_csv(data_dir / "scraped_listings.csv", index=False)
        print(f"Saved {len(df)} listings to {data_dir / 'scraped_listings.csv'}")
        
        # Create calendar-style data for analysis
        calendar_data = []
        for _, listing in df.iterrows():
            if listing['price'] is not None:
                calendar_data.append({
                    'listing_id': listing['listing_id'],
                    'date': datetime.now().date(),  # For demo purposes
                    'price': f"R${listing['price']:.2f}",
                    'available': 't'
                })
        
        if calendar_data:
            calendar_df = pd.DataFrame(calendar_data)
            calendar_df.to_csv(data_dir / "scraped_calendar.csv", index=False)
            print(f"Created calendar data with {len(calendar_df)} entries")
        
        # Create listings-style data
        listings_data = []
        for _, listing in df.iterrows():
            listings_data.append({
                'id': listing['listing_id'],
                'name': listing.get('title', ''),
                'room_type': listing.get('room_type', ''),
                'price': listing.get('price', ''),
                'rating': listing.get('rating', ''),
                'scraped_at': listing.get('scraped_at', '')
            })
        
        if listings_data:
            listings_df = pd.DataFrame(listings_data)
            listings_df.to_csv(data_dir / "scraped_listings_detail.csv", index=False)
            print(f"Created detailed listings data with {len(listings_df)} entries")

def load_calendar(data_dir: Path):
    candidates = [
        data_dir / "calendar.csv", 
        data_dir / "calendar.csv.gz",
        data_dir / "scraped_calendar.csv"  # Support scraped data
    ]
    for p in candidates:
        if p.exists():
            cal = pd.read_csv(p, parse_dates=["date"])
            return cal
    raise FileNotFoundError("Could not find calendar.csv, calendar.csv.gz, or scraped_calendar.csv in data dir")

def load_listings_optional(data_dir: Path):
    candidates = [
        data_dir / "listings.csv", 
        data_dir / "listings.csv.gz",
        data_dir / "scraped_listings_detail.csv"  # Support scraped data
    ]
    for p in candidates:
        if p.exists():
            return pd.read_csv(p, low_memory=False)
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="./data", help="Folder with calendar/listings CSVs")
    parser.add_argument("--start", type=str, default=None, help="Start date YYYY-MM-DD (defaults to Oct 1 current year)")
    parser.add_argument("--end", type=str, default=None, help="End date YYYY-MM-DD (defaults to Nov 30 current year)")
    parser.add_argument("--only_booked", action="store_true", help="Compute stats only on booked nights (available==False)")
    
    # Scraping arguments
    parser.add_argument("--scrape", action="store_true", help="Enable web scraping mode")
    parser.add_argument("--location", type=str, default="Belém, PA", help="Location to search for Airbnb listings")
    parser.add_argument("--checkin", type=str, default=None, help="Check-in date for scraping (YYYY-MM-DD)")
    parser.add_argument("--checkout", type=str, default=None, help="Check-out date for scraping (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=1, help="Number of adults for booking search")
    parser.add_argument("--max-pages", type=int, default=3, help="Maximum pages to scrape")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path("./output")
    charts_dir = out_dir / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)

    start, end = (args.start, args.end)
    if not start or not end:
        start, end = infer_default_window()
    
    # Handle scraping mode
    if args.scrape:
        if not SCRAPING_AVAILABLE:
            print("Scraping dependencies not available. Install with:")
            print("pip install selenium beautifulsoup4 requests")
            print("Also make sure chromedriver is installed and in PATH")
            sys.exit(1)
        
        print("=== WEB SCRAPING MODE ===")
        print("EDUCATIONAL USE ONLY - Please respect robots.txt and terms of service")
        
        checkin = args.checkin or start
        checkout = args.checkout or end
        
        scraper = AirbnbScraper(headless=args.headless)
        
        try:
            listings = scraper.scrape_search_results(
                location=args.location,
                checkin=checkin,
                checkout=checkout,
                adults=args.adults,
                max_pages=args.max_pages
            )
            
            if listings:
                scraper.save_scraped_data(listings, data_dir)
                print(f"\n=== SCRAPING COMPLETED ===")
                print(f"Scraped {len(listings)} listings")
                print(f"Data saved to {data_dir}")
                print("You can now run the analysis on scraped data:")
                print(f"python {sys.argv[0]} --data-dir {data_dir}")
            else:
                print("No listings were scraped. Check your search parameters and try again.")
                sys.exit(1)
                
        except Exception as e:
            print(f"Scraping failed: {e}")
            sys.exit(1)
        
        return  # Exit after scraping

    # Existing analysis code starts here
    # Load data
    cal = load_calendar(data_dir)
    if "date" not in cal.columns:
        print("calendar.csv must have a 'date' column", file=sys.stderr)
        sys.exit(2)

    # Normalize price
    price_col = "price_num"
    if "price" in cal.columns:
        cal[price_col] = cal["price"].apply(to_float_price)
    elif "adjusted_price" in cal.columns:
        cal[price_col] = cal["adjusted_price"].apply(to_float_price)
    else:
        # try generic 'price' like numeric already
        price_candidates = [c for c in cal.columns if "price" in c.lower()]
        if price_candidates:
            cal[price_col] = pd.to_numeric(cal[price_candidates[0]], errors="coerce")
        else:
            cal[price_col] = pd.NA

    # Normalize availability (InsideAirbnb uses 't'/'f' strings)
    if "available" in cal.columns:
        cal["is_available"] = cal["available"].astype(str).str.lower().isin(["t","true","1"])
    else:
        cal["is_available"] = True  # assume sellable unless told otherwise

    # Filter window
    mask = (cal["date"] >= pd.to_datetime(start)) & (cal["date"] <= pd.to_datetime(end))
    win = cal.loc[mask].copy()
    if args.only_booked:
        win = win.loc[~win["is_available"]]

    # Basic guards
    if win.empty:
        print(f"No calendar rows found between {start} and {end}.", file=sys.stderr)
        sys.exit(0)

    # Per-listing stats for Oct–Nov
    grp = win.groupby("listing_id", dropna=True)
    per_listing = grp[price_col].agg(
        nights="count",
        mean_price="mean",
        median_price="median",
        p25=lambda s: s.quantile(0.25),
        p75=lambda s: s.quantile(0.75),
    ).reset_index()

    # Overall summary
    overall = pd.DataFrame({
        "period_start": [start],
        "period_end": [end],
        "listings_active": [per_listing["listing_id"].nunique()],
        "nights": [int(per_listing["nights"].sum())],
        "mean_price": [float(win[price_col].mean())],
        "median_price": [float(win[price_col].median())],
        "p25_price": [float(win[price_col].quantile(0.25))],
        "p75_price": [float(win[price_col].quantile(0.75))],
    })

    # Daily series
    daily = win.groupby("date")[price_col].agg(["mean","median","count"]).reset_index()
    daily.rename(columns={"mean":"avg_price", "median":"median_price", "count":"observations"}, inplace=True)

    # Optional joins for room_type / neighbourhood splits
    lst = load_listings_optional(data_dir)
    if lst is not None:
        # room_type
        if "room_type" in lst.columns:
            rt = win.merge(lst[["id","room_type"]].rename(columns={"id":"listing_id"}), on="listing_id", how="left")
            room_split = rt.groupby("room_type").agg({
                "listing_id": ["nunique", "count"],
                price_col: ["mean", "median"]
            })
            room_split.columns = ["listings", "nights", "mean_price", "median_price"]
            room_split = room_split.reset_index().sort_values("listings", ascending=False)
        else:
            room_split = pd.DataFrame()

        # neighbourhood
        ncol = None
        for c in lst.columns:
            if "neighbourhood" in c.lower() and "cleansed" in c.lower():
                ncol = c; break
        if ncol:
            nh = win.merge(lst[["id", ncol]].rename(columns={"id":"listing_id", ncol:"neighbourhood"}), on="listing_id", how="left")
            nh_split = nh.groupby("neighbourhood").agg({
                "listing_id": ["nunique", "count"],
                price_col: ["mean", "median"]
            })
            nh_split.columns = ["listings", "nights", "mean_price", "median_price"]
            nh_split = nh_split.reset_index().sort_values("listings", ascending=False)
        else:
            nh_split = pd.DataFrame()
    else:
        room_split = pd.DataFrame()
        nh_split = pd.DataFrame()

    # Save outputs
    overall.to_csv(out_dir / "prices_summary.csv", index=False)
    daily.to_csv(out_dir / "daily_avg_price.csv", index=False)
    per_listing.to_csv(out_dir / "listing_avg_price_oct_nov.csv", index=False)
    if not room_split.empty:
        room_split.to_csv(out_dir / "price_roomtype.csv", index=False)
    if not nh_split.empty:
        nh_split.to_csv(out_dir / "price_neighbourhood.csv", index=False)

    # Define search parameters
    currency = "BRL"  # Currency for the search
    check_in = "2025-11-10"  # Check-in date
    check_out = "2025-11-21"  # Check-out date
    ne_lat = -1.3742  # North-East latitude (Belém do Pará area)
    ne_long = -48.4458  # North-East longitude
    sw_lat = -1.5242  # South-West latitude
    sw_long = -48.5458  # South-West longitude
    zoom_value = 1  # Zoom level for the map
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

if __name__ == "__main__":
    main()
