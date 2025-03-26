# src/scrapers/google_search_scraper.py
import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urlparse, urlencode
from dotenv import load_dotenv

# Use absolute import for logger
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

class GoogleSearchScraper:
    def __init__(self, api_key: str = None, cx: str = None):
        """
        Initialize Google Custom Search Scraper
        
        :param api_key: Google Custom Search API Key
        :param cx: Google Custom Search Engine ID
        """
        self.logger = setup_logger('google_search_scraper')
        self.api_key = api_key or os.getenv('GOOGLE_SEARCH_API_KEY')
        self.cx = cx or os.getenv('GOOGLE_SEARCH_CX')
        
        if not self.api_key or not self.cx:
            raise ValueError("Google Search API Key and Custom Search Engine ID are required. "
                             "Please set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX in .env file.")

    def search(self, 
               query: str, 
               num_results: int = 10, 
               business_type: str = None) -> List[Dict]:
        """
        Perform Google Search and extract business information
        
        :param query: Search query
        :param num_results: Number of results to retrieve
        :param business_type: Optional business type filter
        :return: List of business search results
        """
        try:
            # Construct full query with optional business type
            full_query = f"{query} {business_type}" if business_type else query
            
            # Google Custom Search API parameters
            params = {
                'key': self.api_key,
                'cx': self.cx,
                'q': full_query,
                'num': num_results
            }
            
            # Make API request
            response = requests.get(
                'https://www.googleapis.com/customsearch/v1', 
                params=params
            )
            response.raise_for_status()
            
            # Parse search results
            search_results = response.json().get('items', [])
            
            # Process and enrich results
            processed_results = []
            for result in search_results:
                try:
                    processed_result = {
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'snippet': result.get('snippet', ''),
                        'domain': urlparse(result.get('link', '')).netloc
                    }
                    
                    # Additional enrichment could be added here
                    processed_results.append(processed_result)
                except Exception as e:
                    self.logger.warning(f"Error processing individual result: {e}")
            
            return processed_results
        
        except requests.RequestException as e:
            self.logger.error(f"Google Search API request failed: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in search: {e}")
            return []

    def extract_business_details(self, url: str) -> Dict:
        """
        Extract detailed business information from a website
        
        :param url: Website URL to scrape
        :return: Dictionary of business details
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Basic website information extraction
            details = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'meta_description': soup.find('meta', attrs={'name': 'description'})['content'] 
                                    if soup.find('meta', attrs={'name': 'description'}) 
                                    else ''
            }
            
            return details
        
        except requests.RequestException as e:
            self.logger.warning(f"Could not fetch website details for {url}: {e}")
            return {}