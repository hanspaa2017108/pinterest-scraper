"""Setup script for the pinterest-scraper package."""


from setuptools import setup, find_packages

# The setup.py is provided for backwards compatibility
# Modern Python packaging uses pyproject.toml

setup(
    name="pinterest-scrapper",
    version="0.1.0",
    description="A Python package for scraping images from Pinterest",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Aman Hanspal",
    author_email="your.email@example.com",
    url="https://github.com/hanspaa2017108/pinterest-scraper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="pinterest, scraper, images, web scraping, playwright",
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.30.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pinterest-scrapper=pinterest_scraper.cli:main",
        ],
    },
)