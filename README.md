# Pinterest Scrapper

A Python package for scraping images from Pinterest using Playwright with CLI functionality.
https://pypi.org/project/pinterest-scrapper/1/

## Features

- Search Pinterest for images with customizable queries
- Authenticate to access additional content (optional)
- Save search results as JSON files with image URLs, pin URLs, and descriptions
- Download images with customizable naming schemes
- Generate HTML galleries to view downloaded images
- Rate limit handling and retry mechanisms
- Command-line interface for easy usage
- Persistent browser sessions for better performance

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install from PyPI

```bash
pip install pinterest-scrapper
```

### Install from source

```bash
git clone https://github.com/hanspaa2017108/pinterest-scraper.git
pip install -e .
```

### Install Playwright browsers

After installing the package, you need to install the Playwright browsers:

```bash
playwright install chromium
```

## Usage

### Command Line Interface

#### Interactive Mode

```bash
pinterest-scrapper interactive
```

This will guide you through the scraping process with interactive prompts.

#### Direct Scraping

```bash
pinterest-scrapper scrape "indoor plants" --max-pins 200 --download --category plants
```

#### Full Options

```bash
pinterest-scrapper scrape "search query" \
  --max-pins 300 \            # Maximum number of pins to collect
  --max-scrolls 50 \          # Maximum number of page scrolls
  --scroll-pause 2.0 \        # Pause time between scrolls in seconds
  --output "my_output_dir" \  # Custom output directory
  --user-data-dir "browser_data" \  # Directory for browser user data
  --email "your@email.com" \  # Pinterest account email for login
  --password "yourpassword" \ # Pinterest account password for login
  --download \                # Download images
  --category "custom_name" \  # Filename prefix for downloaded images
  --limit 50                  # Limit number of images to download
```

### Python API

```python
import asyncio
from pinterest_scrapper import PinterestScraper

async def main():
    # Initialize the scraper
    scraper = await PinterestScraper().initialize()
    
    try:
        # Optional: Log in to Pinterest
        await scraper.login("your@email.com", "yourpassword")
        
        # Scrape search results
        results = await scraper.scrape_search(
            query="home decor",
            max_pins=100,
            output_dir="pinterest_data"
        )
        
        # Download images
        if results:
            await scraper.download_images(
                data=results,
                folder="pinterest_data/images",
                category_name="home_decor",
                limit=50
            )
            
            # Create HTML gallery
            await scraper.create_image_index(
                folder="pinterest_data/images",
                category_name="home_decor",
                total_images=50
            )
    
    finally:
        # Close the browser
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Notes

- Pinterest may change its website structure over time, which could break this scraper.
- Use this package responsibly and respect Pinterest's terms of service.
- Add delays between requests to avoid IP bans.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
