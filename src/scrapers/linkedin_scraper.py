import os
import re
import requests
from typing import List, Dict
from dotenv import load_dotenv
from bs4 import BeautifulSoup  # Ensure you have beautifulsoup4 installed

# Use absolute import for logger
from src.utils.logger import setup_logger

class LinkedInProfileScraper:
    def __init__(self, api_key: str = None):
        """
        Initialize LinkedIn Profile Scraper

        :param api_key: Optional Google Search API Key
        """
        self.logger = setup_logger('linkedin_profile_scraper')
        self.api_key = api_key or os.getenv('GOOGLE_SEARCH_API_KEY')
        self.cx = os.getenv('GOOGLE_SEARCH_CX')

        if not self.api_key or not self.cx:
            raise ValueError("Google Search API Key and Custom Search Engine ID are required")

    def find_profiles(self,
                      company_name: str,
                      location: str = None,
                      num_results: int = 5) -> List[Dict]:
        """
        Find LinkedIn profiles for a specific company

        :param company_name: Name of the company
        :param location: Optional location filter
        :param num_results: Number of results to retrieve
        :return: List of LinkedIn profile links
        """
        try:
            # Clean company name for better search
            clean_company_name = re.sub(r'[^a-zA-Z0-9\s]', '', company_name)

            # Construct search query with multiple strategies
            queries = [
                f"site:linkedin.com/in \"{clean_company_name}\"",
                f"site:linkedin.com/in {clean_company_name.replace(' ', '-').lower()}",
                f"site:linkedin.com/in {clean_company_name.split()[0]}"
            ]

            linkedin_profiles = []
            for query in queries:
                if location:
                    query += f" {location}"

                params = {
                    'key': self.api_key,
                    'cx': self.cx,
                    'q': query,
                    'num': num_results
                }

                response = requests.get(
                    'https://www.googleapis.com/customsearch/v1',
                    params=params
                )
                response.raise_for_status()

                search_results = response.json().get('items', [])

                for result in search_results:
                    try:
                        profile_url = result.get('link', '')
                        if '/in/' in profile_url and profile_url not in [p['profile_url'] for p in linkedin_profiles]:
                            profile_info = {
                                'name': self._extract_name_from_url(profile_url),
                                'profile_url': profile_url,
                                'title': result.get('title', ''),
                                'snippet': result.get('snippet', '')
                            }
                            linkedin_profiles.append(profile_info)
                    except Exception as e:
                        self.logger.warning(f"Error processing profile: {e}")

                if len(linkedin_profiles) >= num_results:
                    break

            if not linkedin_profiles:
                self.logger.warning(f"No LinkedIn profiles found for {company_name}")

            return linkedin_profiles[:num_results]

        except requests.RequestException as e:
            self.logger.error(f"LinkedIn profile search failed: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in LinkedIn profile search: {e}")
            return []

    def _extract_name_from_url(self, url: str) -> str:
        """
        Extract profile name from LinkedIn URL

        :param url: LinkedIn profile URL
        :return: Extracted name
        """
        try:
            name_part = url.split('/in/')[-1].replace('-', ' ').title()
            return name_part
        except Exception as e:
            self.logger.warning(f"Could not extract name from URL {url}: {e}")
            return ''

    def extract_linkedin_details(self, profile_url: str) -> Dict:
        """
        Enhanced LinkedIn profile information extraction

        :param profile_url: URL of the LinkedIn profile to extract details from
        :return: Dictionary containing extracted profile details:
            - full_name: Full name of the individual
            - current_title: Current professional title
            - company_experience: List of past or current positions/companies
            - skills: List of skills mentioned on the profile
            - education: List of education entries
        """
        details = {
            'full_name': '',
            'current_title': '',
            'company_experience': [],
            'skills': [],
            'education': []
        }
        try:
            headers = {
                "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/90.0.4430.93 Safari/537.36")
            }
            response = requests.get(profile_url, headers=headers)
            response.raise_for_status()
            html = response.text

            soup = BeautifulSoup(html, "html.parser")

            # Extract full name (example: from a header element)
            name_tag = soup.find("h1")
            if name_tag:
                details['full_name'] = name_tag.get_text(strip=True)

            # Extract current title (example: from a subtitle div)
            title_tag = soup.find("div", class_="top-card-layout__headline")
            if title_tag:
                details['current_title'] = title_tag.get_text(strip=True)

            # Extract company experience (example: list items in an 'experience' section)
            exp_section = soup.find(id="experience")
            if exp_section:
                exp_items = exp_section.find_all("li")
                details['company_experience'] = [item.get_text(strip=True) for item in exp_items]

            # Extract skills (example: span elements with class 'skill')
            skills_tags = soup.find_all("span", class_="skill")
            details['skills'] = [tag.get_text(strip=True) for tag in skills_tags]

            # Extract education (example: list items in an 'education' section)
            edu_section = soup.find(id="education")
            if edu_section:
                edu_items = edu_section.find_all("li")
                details['education'] = [item.get_text(strip=True) for item in edu_items]

        except Exception as e:
            self.logger.error(f"Error extracting LinkedIn details from {profile_url}: {e}")

        return details
