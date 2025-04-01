import os
import json
from datetime import datetime
import string
import random

def sanitize_filename(filename):
    """
    Sanitize a filename to ensure it's valid across operating systems.
    
    Args:
        filename (str): The filename to sanitize
        
    Returns:
        str: A sanitized filename
    """
    # Replace spaces with underscores
    sanitized = filename.replace(' ', '_')
    
    # Remove invalid characters
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized = ''.join(c for c in sanitized if c in valid_chars)
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized

def get_output_dir(query=None):
    """
    Generate an output directory name with timestamp and optional query.
    
    Args:
        query (str, optional): Search query to include in directory name
        
    Returns:
        str: Path to output directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if query:
        # Sanitize query for folder name
        query_part = sanitize_filename(query)
        dir_name = f"pinterest_{query_part}_{timestamp}"
    else:
        dir_name = f"pinterest_data_{timestamp}"
    
    # Create directory if it doesn't exist
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    return dir_name

def save_json(data, filename):
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save (must be JSON-serializable)
        filename (str): Filename to save to
    """
    # Create directory if it doesn't exist
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Data saved to {filename}")

def load_json(filename):
    """
    Load data from a JSON file.
    
    Args:
        filename (str): Filename to load from
        
    Returns:
        The loaded data, or None if the file doesn't exist
    """
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def generate_user_agent():
    """
    Generate a random user agent string.
    
    Returns:
        str: A user agent string
    """
    os_versions = [
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "X11; Linux x86_64"
    ]
    
    chrome_versions = [
        "115.0.0.0",
        "114.0.0.0",
        "113.0.0.0",
        "112.0.0.0"
    ]
    
    os_choice = random.choice(os_versions)
    chrome_version = random.choice(chrome_versions)
    
    return f"Mozilla/5.0 ({os_choice}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"

def create_browser_config(user_data_dir=None):
    """
    Create a configuration dictionary for browser initialization.
    
    Args:
        user_data_dir (str, optional): Directory for persistent browser data
        
    Returns:
        dict: Browser configuration
    """
    config = {
        "headless": True,  # Always run in headless mode
        "user_data_dir": user_data_dir,
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": generate_user_agent(),
        "locale": "en-US",
        "timezone_id": "America/New_York",
    }
    
    return config