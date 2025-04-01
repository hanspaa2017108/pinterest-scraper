"""
Pinterest Scrapper - A Python package for scraping images from Pinterest.

This package provides tools to search and download images from Pinterest using
Playwright for automated browser interactions.
"""

from .scraper import PinterestScraper
from . import utils

__version__ = "1"
__author__ = "Aman Hanspal"

# Export main classes and functions
__all__ = ["PinterestScraper"]