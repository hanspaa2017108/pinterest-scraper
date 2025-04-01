import asyncio
import argparse
import os
import sys
import getpass
from datetime import datetime

from .scraper import PinterestScraper
from .utils import get_output_dir

async def interactive_mode():
    """Run the Pinterest scraper in interactive mode with CLI prompts"""
    print("Pinterest Scrapper Interactive Mode")
    print("=================================\n")
    
    # Create a user_data_dir for persistent sessions
    user_data_dir = os.path.join(os.getcwd(), "pinterest_browser_data")
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Initialize the scraper
    print("\nInitializing scraper...")
    scraper = await PinterestScraper(user_data_dir=user_data_dir).initialize()
    
    try:
        # Check if already logged in
        if not await scraper.check_login_status():
            # Ask for login credentials
            login_choice = input("Would you like to log in to Pinterest? (y/n): ").lower()
            if login_choice.startswith('y'):
                email = input("Enter your Pinterest email: ")
                password = getpass.getpass("Enter your Pinterest password: ")
                
                login_success = await scraper.login(email, password)
                if not login_success:
                    print("Login was not successful. Continuing without authentication.")
        
        # Allow multiple queries
        while True:
            query = input("\nEnter a search query (or 'exit' to quit): ")
            if query.lower() == 'exit':
                break
            
            max_pins = int(input("Maximum number of pins to collect (recommended: 100-500): ") or "300")
            
            # Create output directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"pinterest_data_{timestamp}"
            
            # Scrape pins
            results = await scraper.scrape_search(query, max_pins=max_pins, output_dir=output_dir)
            
            if results:
                # Ask if user wants to download the images
                download_choice = input("Do you want to download the images? (y/n): ").lower()
                if download_choice.startswith('y'):
                    # Ask for category name for downloaded images
                    category_name = input("Enter a category name for the images (e.g. 'fashion'): ")
                    
                    # Get number of images to download
                    limit_input = input("How many images to download? (Enter a number or press Enter for all): ")
                    limit = int(limit_input) if limit_input.strip() else None
                    
                    # Create images directory
                    images_dir = f"{output_dir}/images"
                    
                    # Download images with custom naming
                    await scraper.download_images(results, images_dir, category_name, limit)
                    
                    # Create an index.html file to easily view the images
                    total_images = limit if limit else len(results)
                    await scraper.create_image_index(images_dir, category_name, total_images)
                    
                    print(f"Images downloaded with naming pattern: {category_name}-1, {category_name}-2, etc.")
            
            continue_choice = input("Do you want to scrape another query? (y/n): ").lower()
            if not continue_choice.startswith('y'):
                break
    
    finally:
        # Close the browser
        await scraper.close()
        print("Scraper closed.")


async def scrape_with_args(args):
    """Run the Pinterest scraper with command line arguments"""
    # Create a user_data_dir for persistent sessions
    user_data_dir = args.user_data_dir or os.path.join(os.getcwd(), "pinterest_browser_data")
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Initialize the scraper
    print(f"Initializing scraper...")
    scraper = await PinterestScraper(user_data_dir=user_data_dir).initialize()
    
    try:
        # Handle login if credentials provided
        if args.email and args.password:
            print("Logging in with provided credentials...")
            login_success = await scraper.login(args.email, args.password)
            if not login_success:
                print("Login was not successful. Continuing without authentication.")
        else:
            # Check if already logged in from previous session
            await scraper.check_login_status()
        
        # Create output directory
        output_dir = args.output or get_output_dir(args.query)
        
        # Scrape pins
        print(f"Scraping '{args.query}' (max pins: {args.max_pins})...")
        results = await scraper.scrape_search(
            args.query, 
            max_pins=args.max_pins, 
            max_scrolls=args.max_scrolls,
            scroll_pause_time=args.scroll_pause,
            output_dir=output_dir
        )
        
        if results and args.download:
            # Create images directory
            images_dir = os.path.join(output_dir, "images")
            
            # Download images
            limit = args.limit if args.limit > 0 else None
            await scraper.download_images(results, images_dir, args.category, limit)
            
            # Create index for the gallery
            total_images = limit if limit else len(results)
            await scraper.create_image_index(images_dir, args.category, total_images)
            
            print(f"Images downloaded to {images_dir}")
    
    finally:
        # Close the browser
        await scraper.close()
        print("Scraper closed.")


def main():
    """Main entry point for the command line interface"""
    parser = argparse.ArgumentParser(description="Pinterest Image Scraper")
    
    # Add subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Run in interactive mode with prompts")
    
    # Scrape mode
    scrape_parser = subparsers.add_parser("scrape", help="Run with specified parameters")
    scrape_parser.add_argument("query", help="Search query")
    scrape_parser.add_argument("--max-pins", type=int, default=300, help="Maximum number of pins to collect")
    scrape_parser.add_argument("--max-scrolls", type=int, default=50, help="Maximum number of page scrolls")
    scrape_parser.add_argument("--scroll-pause", type=float, default=2.0, help="Pause time between scrolls in seconds")
    scrape_parser.add_argument("--output", help="Output directory")
    scrape_parser.add_argument("--user-data-dir", help="Directory for browser user data")
    scrape_parser.add_argument("--email", help="Pinterest account email for login")
    scrape_parser.add_argument("--password", help="Pinterest account password for login")
    scrape_parser.add_argument("--download", action="store_true", help="Download images")
    scrape_parser.add_argument("--category", default="pinterest", help="Filename prefix for downloaded images")
    scrape_parser.add_argument("--limit", type=int, default=0, help="Limit number of images to download (0 for all)")
    
    args = parser.parse_args()
    
    # Default to interactive mode if no command provided
    if not args.command:
        args.command = "interactive"
    
    if args.command == "interactive":
        asyncio.run(interactive_mode())
    elif args.command == "scrape":
        asyncio.run(scrape_with_args(args))


if __name__ == "__main__":
    main()