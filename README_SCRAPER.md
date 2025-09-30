# Belém Price Analysis with Web Scraping

This project analyzes Airbnb pricing data for Belém, PA, and includes web scraping capabilities for educational purposes.

## Features

- **Data Analysis**: Analyze existing Airbnb data (InsideAirbnb format)
- **Web Scraping**: Scrape Airbnb listings for educational purposes
- **Price Analytics**: Generate comprehensive price statistics and visualizations
- **Export Data**: Save results to CSV and generate charts

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. For web scraping, you'll also need Chrome and ChromeDriver:
```bash
# On Ubuntu/Debian:
sudo apt-get install chromium-browser chromium-chromedriver

# On macOS with Homebrew:
brew install --cask google-chrome
brew install chromedriver

# On Windows, download ChromeDriver from:
# https://chromedriver.chromium.org/
```

## Usage

### 1. Simple Sample Data Generation (Recommended for Testing)

Generate sample data for educational purposes:

```bash
python simple_airbnb_scraper.py --location "Belém, PA" --pages 2
```

### 2. Web Scraping Mode (Educational Use Only)

**Important**: This is for educational purposes only. Please respect robots.txt and Airbnb's terms of service.

```bash
# Scrape Airbnb data
python belem_price_analysis.py --scrape --location "Belém, PA" --checkin 2025-10-01 --checkout 2025-11-30 --max-pages 3
```

Parameters:
- `--location`: Location to search (e.g., "Belém, PA")
- `--checkin`: Check-in date (YYYY-MM-DD)
- `--checkout`: Check-out date (YYYY-MM-DD)
- `--adults`: Number of adults (default: 1)
- `--max-pages`: Maximum pages to scrape (default: 3)
- `--headless`: Run browser in headless mode

### 3. Data Analysis Mode

After scraping or with existing data:

```bash
# Analyze scraped data
python belem_price_analysis.py --data-dir ./data

# Analyze with custom date range
python belem_price_analysis.py --data-dir ./data --start 2025-10-01 --end 2025-11-30

# Analyze only booked nights
python belem_price_analysis.py --data-dir ./data --only_booked
```

## Output Files

The analysis generates several output files in the `./output` directory:

- `prices_summary.csv`: Overall price statistics
- `daily_avg_price.csv`: Daily average prices
- `listing_avg_price_oct_nov.csv`: Per-listing statistics
- `price_roomtype.csv`: Prices by room type
- `price_neighbourhood.csv`: Prices by neighborhood
- `charts/daily_avg_price.png`: Daily price trends chart
- `charts/price_box_oct_nov.png`: Price distribution boxplot

## Data Format

The scraper generates data compatible with InsideAirbnb format:

### Calendar Data (calendar.csv)
```csv
listing_id,date,price,available
1,2025-10-01,R$120.00,t
1,2025-10-02,R$120.00,f
```

### Listings Data (listings.csv)
```csv
id,name,room_type,price,rating
1,"Apartamento no centro",Casa inteira,120.0,4.5
```

## Educational Purpose Notice

This web scraper is designed for educational purposes only to demonstrate web scraping techniques. Please ensure you:

1. **Respect robots.txt**: Check and follow the website's robots.txt file
2. **Follow Terms of Service**: Respect the website's terms of service
3. **Use Rate Limiting**: The scraper includes delays to avoid overloading servers
4. **Consider APIs**: Use official APIs when available instead of scraping
5. **Local Development**: Use primarily for learning and local development

## Legal and Ethical Considerations

- **Educational Use Only**: This tool is for learning web scraping concepts
- **Respect Website Policies**: Always check and follow robots.txt and terms of service
- **Rate Limiting**: Built-in delays prevent server overload
- **Data Usage**: Use scraped data responsibly and in compliance with applicable laws
- **Alternative Sources**: Consider using official APIs or public datasets when available

## Troubleshooting

### ChromeDriver Issues
If you get ChromeDriver errors:
1. Make sure Chrome is installed
2. Install ChromeDriver and add to PATH
3. Try running in headless mode: `--headless`

### Scraping Failures
If scraping fails:
1. Use the simple scraper for sample data: `python simple_airbnb_scraper.py`
2. Check your internet connection
3. Verify the location name is correct
4. Try reducing `--max-pages`

### Missing Dependencies
Install all requirements:
```bash
pip install pandas matplotlib requests beautifulsoup4 selenium
```

## Sample Analysis Workflow

1. **Generate Sample Data**:
   ```bash
   python simple_airbnb_scraper.py --location "Belém, PA"
   ```

2. **Run Analysis**:
   ```bash
   python belem_price_analysis.py --data-dir ./data
   ```

3. **View Results**:
   - Check `./output/` directory for CSV files and charts
   - Review price trends and statistics

## Contributing

This is an educational project. Contributions should focus on:
- Improving data analysis capabilities
- Adding more visualization options
- Enhancing the educational aspects
- Ensuring ethical scraping practices

## License

This project is for educational purposes. Please respect all applicable laws and website terms of service when using web scraping functionality.
