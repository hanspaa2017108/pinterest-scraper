import asyncio
import json
import os
import random
import time
from datetime import datetime
from urllib.parse import quote
import aiohttp
from playwright.async_api import async_playwright

class PinterestScraper:
    """
    A class for scraping Pinterest using Playwright.
    
    Attributes:
        user_data_dir (str): Directory to store browser user data for persistent sessions
        browser: Playwright browser instance
        context: Playwright browser context
        page: Playwright page
        session_start_time: When the current session started
        query_count: Number of queries made in this session
        rate_limit_delay: Seconds to wait if rate limited
        is_authenticated: Whether the user is authenticated with Pinterest
    """
    
    def __init__(self, user_data_dir=None):
        """
        Initialize the PinterestScraper.
        
        Args:
            user_data_dir (str): Directory to store browser user data for persistent sessions
        """
        self.user_data_dir = user_data_dir
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.session_start_time = datetime.now()
        self.query_count = 0
        self.rate_limit_delay = 30  # seconds to wait if rate limited
        self.is_authenticated = False
    
    async def initialize(self):
        """
        Initialize the browser and context.
        
        Returns:
            PinterestScraper: The initialized scraper instance
        """
        self.playwright = await async_playwright().start()
        
        # Browser and context options
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "color_scheme": "light",
            "device_scale_factor": 1.0,
            "is_mobile": False,
        }
        
        # Different initialization based on whether we use persistent context
        if self.user_data_dir:
            # Using persistent context
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=True,
                **context_options
            )
            self.browser = None  # No separate browser object when using persistent context
        else:
            # Regular browser + context
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(**context_options)
        
        # Add scripts to evade detection
        await self.context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        """)
        
        # Create a page
        self.page = await self.context.new_page()
        
        # Set default timeout
        self.page.set_default_timeout(30000)
        
        return self
    
    async def close(self):
        """Close the browser and clean up"""
        if self.context:
            await self.context.close()
        if self.browser:  # Only if we created a separate browser
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def _random_sleep(self, min_seconds=1, max_seconds=3):
        """
        Sleep for a random amount of time to appear more human-like.
        
        Args:
            min_seconds (float): Minimum sleep time in seconds
            max_seconds (float): Maximum sleep time in seconds
        """
        await asyncio.sleep(random.uniform(min_seconds, max_seconds))
    
    async def _random_scroll(self, min_pixels=400, max_pixels=800):
        """
        Scroll a random amount.
        
        Args:
            min_pixels (int): Minimum scroll amount in pixels
            max_pixels (int): Maximum scroll amount in pixels
        """
        pixels = random.randint(min_pixels, max_pixels)
        await self.page.evaluate(f"window.scrollBy(0, {pixels})")
    
    async def _human_like_scroll_to_bottom(self):
        """Scroll to bottom in a more human-like way with random pauses"""
        current_scroll_position = 0
        new_height = await self.page.evaluate("document.body.scrollHeight")
        
        # Random scroll until we reach the bottom
        while current_scroll_position < new_height:
            # Random scroll amount
            scroll_step = random.randint(300, 700)
            current_scroll_position += scroll_step
            
            # Don't scroll past the bottom
            if current_scroll_position > new_height:
                current_scroll_position = new_height
            
            # Execute scroll
            await self.page.evaluate(f"window.scrollTo(0, {current_scroll_position})")
            
            # Random pause
            await self._random_sleep(0.5, 2)
    
    async def _handle_login_prompt(self):
        """Handle login prompts or popups that might appear"""
        try:
            # Check for login popup
            login_popup = await self.page.query_selector('div[data-test-id="login-modal"]')
            if login_popup:
                # Find the close button (X) and click it
                close_btn = await self.page.query_selector('button[aria-label="Close"]')
                if close_btn:
                    await close_btn.click()
                    await self._random_sleep(1, 2)
            
            # Check for cookie consent
            cookie_btn = await self.page.query_selector('button[data-test-id="cookie-banner-accept-button"]')
            if cookie_btn:
                await cookie_btn.click()
                await self._random_sleep(1, 2)
            
            # Check for other common popups and close them
            close_buttons = await self.page.query_selector_all('button[aria-label="Close"]')
            for button in close_buttons:
                await button.click()
                await self._random_sleep(0.5, 1)
        
        except Exception as e:
            print(f"Error handling popups: {e}")
    
    async def login(self, email, password):
        """
        Log in to Pinterest.
        
        Args:
            email (str): Pinterest account email
            password (str): Pinterest account password
            
        Returns:
            bool: Whether login was successful
        """
        print("Attempting to log in to Pinterest...")
        
        try:
            # Navigate to the login page
            await self.page.goto("https://www.pinterest.com/login/", wait_until="domcontentloaded")
            await self._random_sleep(2, 3)
            
            # Handle cookie consent if present
            cookie_btn = await self.page.query_selector('button[data-test-id="cookie-banner-accept-button"]')
            if cookie_btn:
                await cookie_btn.click()
                await self._random_sleep(1, 2)
            
            # Wait for the email field
            await self.page.wait_for_selector('input#email', state='visible')
            
            # Enter email with human-like typing
            await self.page.fill('input#email', email, timeout=5000)
            await self._random_sleep(0.5, 1.5)
            
            # Enter password with human-like typing
            await self.page.fill('input#password', password, timeout=5000)
            await self._random_sleep(0.8, 2)
            
            # Click login button
            login_button = await self.page.query_selector('button[type="submit"]')
            if login_button:
                await login_button.click()
            else:
                print("Login button not found. Trying alternative method...")
                await self.page.keyboard.press('Enter')
            
            # Wait for navigation to complete
            await self.page.wait_for_load_state("networkidle")
            
            # Check if login was successful by looking for the user menu or avatar
            success_selectors = [
                'div[data-test-id="header-profile"]', 
                'div[data-test-id="user-menu"]',
                'button[aria-label="Your profile picture"]',
                'button[data-test-id="header-profile"]'
            ]
            
            for selector in success_selectors:
                success_element = await self.page.query_selector(selector)
                if success_element:
                    print("Login successful!")
                    self.is_authenticated = True
                    return True
            
            # Check for error messages
            error_message = await self.page.query_selector('div[data-test-id="loginError"]')
            if error_message:
                error_text = await error_message.text_content()
                print(f"Login failed: {error_text}")
                return False
            
            print("Login status unclear. Check browser for verification steps or captcha.")
            # Take a screenshot to help debug
            await self.page.screenshot(path="pinterest_login_status.png")
            return False
        
        except Exception as e:
            print(f"Error during login: {e}")
            await self.page.screenshot(path="pinterest_login_error.png")
            return False
    
    async def check_login_status(self):
        """
        Check if we're logged in.
        
        Returns:
            bool: Whether the user is logged in
        """
        try:
            # Navigate to Pinterest homepage
            await self.page.goto("https://www.pinterest.com/", wait_until="domcontentloaded")
            await self._random_sleep(2, 3)
            
            # Check for user menu or avatar
            success_selectors = [
                'div[data-test-id="header-profile"]', 
                'div[data-test-id="user-menu"]',
                'button[aria-label="Your profile picture"]',
                'button[data-test-id="header-profile"]'
            ]
            
            for selector in success_selectors:
                success_element = await self.page.query_selector(selector)
                if success_element:
                    print("Already logged in!")
                    self.is_authenticated = True
                    return True
            
            print("Not logged in.")
            return False
        
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False
    
    async def scrape_search(self, query, max_pins=500, max_scrolls=50, scroll_pause_time=2, output_dir="pinterest_data"):
        """
        Scrape Pinterest search results.
        
        Args:
            query (str): Search query
            max_pins (int): Maximum number of pins to collect
            max_scrolls (int): Maximum number of scrolls
            scroll_pause_time (float): Seconds to pause between scrolls
            output_dir (str): Directory to save results
            
        Returns:
            list: List of dictionaries containing pin data
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Add delay between queries to prevent rate limiting
        self.query_count += 1
        if self.query_count > 1:
            delay = random.uniform(5, 15)  # Random delay between 5-15 seconds between queries
            print(f"Adding delay of {delay:.1f} seconds between queries...")
            await asyncio.sleep(delay)
        
        # Encode query for URL
        encoded_query = quote(query)
        url = f"https://www.pinterest.com/search/pins/?q={encoded_query}&rs=typed"
        
        print(f"Navigating to {url}")
        try:
            # Navigate to Pinterest
            response = await self.page.goto(url, wait_until="domcontentloaded")
            
            # Check for potential blocks or rate limits
            if response.status >= 400:
                print(f"Received status code {response.status}. Possible rate limiting.")
                print("Waiting for rate limit to reset...")
                await asyncio.sleep(self.rate_limit_delay)
                return []
            
            # Wait for content to load
            await self.page.wait_for_load_state("networkidle")
            await self._random_sleep(3, 5)
            
            # Handle any popups or login prompts
            await self._handle_login_prompt()
            
            # Take a screenshot for debugging
            await self.page.screenshot(path=f"{output_dir}/{query}_start.png")
            
            results = []
            processed_urls = set()  # Track processed image URLs to avoid duplicates
            scrolls = 0
            consecutive_no_new = 0
            
            print(f"Starting to scrape up to {max_pins} pins for '{query}'")
            print(f"Authentication status: {'Authenticated' if self.is_authenticated else 'Not authenticated'}")
            
            while len(results) < max_pins and scrolls < max_scrolls and consecutive_no_new < 5:
                # Get current height for comparison later
                last_height = await self.page.evaluate("document.body.scrollHeight")
                
                try:
                    # Wait for pins to load with a reasonable timeout
                    await self.page.wait_for_selector("div[data-test-id='pinWrapper']", 
                                                     state="visible", 
                                                     timeout=10000)
                except:
                    # If we can't find the primary selector, try others
                    print("Primary selector not found, trying alternatives...")
                
                # Try multiple selectors to find pins
                selectors = [
                    "div[data-test-id='pinWrapper']",
                    "div[data-grid-item='true']",
                    "div.GrowthUnauthPinImage",
                    "div.PinCard__Card",
                    "div[role='listitem']"
                ]
                
                pins = []
                for selector in selectors:
                    pins = await self.page.query_selector_all(selector)
                    if pins:
                        print(f"Found {len(pins)} pins with selector: {selector}")
                        break
                
                if not pins:
                    print("No pins found with any selector.")
                    await self.page.screenshot(path=f"{output_dir}/{query}_no_pins_{scrolls}.png")
                    break
                
                # Track new pins in this scroll
                new_pins_count = 0
                
                # Process pins
                for pin in pins:
                    try:
                        # Get image
                        image_element = await pin.query_selector("img")
                        if not image_element:
                            continue
                        
                        image_url = await image_element.get_attribute("src")
                        if not image_url or image_url in processed_urls:
                            continue
                        
                        # Mark as processed
                        processed_urls.add(image_url)
                        
                        # Get title/description
                        title = await image_element.get_attribute("alt") or "No title"
                        
                        # Get link
                        link_element = await pin.query_selector("a")
                        pin_url = await link_element.get_attribute("href") if link_element else ""
                        
                        if pin_url and pin_url.startswith('/'):
                            pin_url = f"https://www.pinterest.com{pin_url}"
                        
                        # Create pin data
                        pin_data = {
                            "title": title,
                            "image_url": image_url,
                            "pin_url": pin_url,
                            "query": query
                        }
                        
                        results.append(pin_data)
                        new_pins_count += 1
                        print(f"Collected {len(results)}/{max_pins} pins")
                        
                        if len(results) >= max_pins:
                            break
                    
                    except Exception as e:
                        print(f"Error processing pin: {e}")
                
                # Human-like scroll
                await self._human_like_scroll_to_bottom()
                
                # Wait for new content to load
                await asyncio.sleep(scroll_pause_time)
                
                # Check if we got new pins
                if new_pins_count == 0:
                    consecutive_no_new += 1
                    print(f"No new pins in this scroll ({consecutive_no_new}/5)")
                else:
                    consecutive_no_new = 0
                
                # Check if scrolling is effective
                new_height = await self.page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    print("Page height didn't change. Might have reached the end.")
                    consecutive_no_new += 1
                
                scrolls += 1
                print(f"Scrolled down {scrolls}/{max_scrolls} times")
            
            # Take final screenshot
            await self.page.screenshot(path=f"{output_dir}/{query}_final.png")
            
            # Save the results to a JSON file
            filename = f"{output_dir}/{query}_pins.json"
            with open(filename, "w") as file:
                json.dump(results, indent=4, fp=file)
            
            print(f"Scraping complete. {len(results)} pins saved to {filename}")
            return results
        
        except Exception as e:
            print(f"Error during scraping: {e}")
            # Save screenshot on error for debugging
            await self.page.screenshot(path=f"{output_dir}/{query}_error.png")
            return []
    
    async def download_images(self, data, folder, category_name=None, limit=None):
        """
        Download images from scraped data with custom naming.
        
        Args:
            data (list): List of pin data dictionaries
            folder (str): Directory to save images
            category_name (str, optional): Custom prefix for image filenames
            limit (int, optional): Maximum number of images to download
        """
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # Use provided category name or ask for one if not provided
        if not category_name:
            category_name = input("Enter a category name for downloaded images (e.g. 'fashion'): ")
            # Remove spaces and special characters from category name
            category_name = "".join([c if c.isalnum() or c == "-" else "_" for c in category_name])
        
        # Limit the number of downloads if specified
        pins_to_download = data[:limit] if limit else data
        total_pins = len(pins_to_download)
        
        print(f"Downloading {total_pins} images to {folder}...")
        print(f"Images will be named as: {category_name}-1, {category_name}-2, ..., {category_name}-{total_pins}")
        
        async with aiohttp.ClientSession() as session:
            for i, pin in enumerate(pins_to_download):
                if 'image_url' in pin and pin['image_url']:
                    try:
                        # Create filename with custom naming scheme
                        filename = f"{folder}/{category_name}-{i+1}.jpg"
                        
                        # Download image
                        async with session.get(pin['image_url']) as response:
                            if response.status == 200:
                                with open(filename, 'wb') as f:
                                    f.write(await response.read())
                                print(f"Downloaded image {category_name}-{i+1} ({i+1}/{total_pins})")
                            else:
                                print(f"Failed to download image {category_name}-{i+1}: HTTP {response.status}")
                        
                        # Add delay between downloads
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                    
                    except Exception as e:
                        print(f"Error downloading image {category_name}-{i+1}: {e}")

    async def create_image_index(self, folder, category_name, total_images):
        """
        Create an index HTML file to easily view downloaded images.
        
        Args:
            folder (str): Directory containing images
            category_name (str): Category name used for naming
            total_images (int): Total number of images
        """
        index_path = f"{folder}/index.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{category_name} Images</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .gallery {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    grid-gap: 15px;
                }}
                .item {{ 
                    border: 1px solid #ddd; 
                    border-radius: 5px; 
                    overflow: hidden;
                    box-shadow: 0 0 5px rgba(0,0,0,0.1);
                }}
                .item img {{ 
                    width: 100%; 
                    height: 200px;
                    object-fit: cover;
                    display: block;
                }}
                .item p {{ 
                    padding: 10px; 
                    margin: 0; 
                    text-align: center; 
                    background: #f9f9f9;
                }}
            </style>
        </head>
        <body>
            <h1>{category_name} Images ({total_images})</h1>
            <div class="gallery">
        """
        
        # Add each image to the gallery
        for i in range(1, total_images + 1):
            image_name = f"{category_name}-{i}.jpg"
            html_content += f"""
                <div class="item">
                    <img src="{image_name}" alt="{image_name}">
                    <p>{image_name}</p>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Write the HTML file
        with open(index_path, "w") as f:
            f.write(html_content)
        
        print(f"Created image gallery index at {index_path}")