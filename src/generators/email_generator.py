# src/generators/email_generator.py
import re
import random
import requests
import dns.resolver
import os
from typing import List, Dict

# Use absolute import for logger
from src.utils.logger import setup_logger

# Conditional OpenAI import to avoid global import
try:
    import openai
except ImportError:
    openai = None

class EmailGenerator:
    def __init__(self, openai_api_key: str = None):
        """
        Initialize Email Generator with OpenAI integration and logging
        
        :param openai_api_key: OpenAI API key
        """
        # Setup logging
        self.logger = setup_logger('email_generator')
        
        # OpenAI API Key setup
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Check OpenAI integration
        if openai and self.openai_api_key:
            try:
                self.client = openai.OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                self.logger.error(f"OpenAI Client initialization failed: {e}")
                self.client = None
        else:
            self.client = None
            if not openai:
                self.logger.warning("OpenAI library not installed")
            if not self.openai_api_key:
                self.logger.warning("OpenAI API Key not found")

    def generate_email_formats(self, 
                                company_name: str, 
                                domain: str, 
                                sample_names: List[str] = None) -> List[str]:
        """
        Generate potential email formats for a company
        
        :param company_name: Name of the company
        :param domain: Company's email domain
        :param sample_names: Optional list of sample names to use
        :return: List of potential email formats
        """
        # Standard email format patterns
        email_formats = [
            "{first}.{last}@{domain}",
            "{first}{last}@{domain}",
            "{first}_{last}@{domain}",
            "{first[0]}{last}@{domain}",
            "{first[0]}.{last}@{domain}",
            "{first}@{domain}"
        ]
        
        # If no sample names provided, generate some
        if not sample_names:
            sample_names = self._generate_sample_names(company_name)
        
        # Generate potential emails
        potential_emails = []
        for name in sample_names:
            for format_pattern in email_formats:
                # Split name into first and last
                name_parts = name.split()
                if len(name_parts) >= 2:
                    first, last = name_parts[0], name_parts[-1]
                    
                    try:
                        email = format_pattern.format(
                            first=first.lower(), 
                            last=last.lower(), 
                            first0=first[0].lower(), 
                            domain=domain
                        )
                        potential_emails.append(email)
                    except Exception as e:
                        self.logger.warning(f"Error generating email: {e}")
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(potential_emails))

    def _generate_sample_names(self, company_name: str, num_names: int = 3) -> List[str]:
        """
        Use OpenAI to generate sample professional names based on company
        
        :param company_name: Name of the company
        :param num_names: Number of names to generate
        :return: List of generated names
        """
        # Check if OpenAI client is available
        if not self.client:
            self.logger.warning("OpenAI client not available. Using fallback names.")
            return [
                "John Smith",
                "Emily Johnson",
                "Michael Brown"
            ]

        try:
            # Prompt for generating professional names
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Generate realistic professional names for employees at a tech company."
                    },
                    {
                        "role": "user", 
                        "content": f"Generate {num_names} professional names that could work at {company_name}. "
                                   "Include first and last names. Format as: FirstName LastName"
                    }
                ],
                max_tokens=100,
                n=1
            )
            
            # Extract and process names
            names_text = response.choices[0].message.content
            names = [name.strip() for name in names_text.split('\n') if name.strip()]
            
            return names
        
        except Exception as e:
            self.logger.error(f"Error generating sample names: {e}")
            
            # Fallback to default names if AI generation fails
            return [
                "John Smith",
                "Emily Johnson",
                "Michael Brown"
            ]

    def validate_email_format(self, email: str) -> bool:
        """
        Validate email format using regex
        
        :param email: Email address to validate
        :return: Whether email format is valid
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def validate_domain(self, email: str) -> bool:
        """
        Validate email domain using DNS lookup
        
        :param email: Email address to validate domain for
        :return: Whether domain has valid MX records
        """
        try:
            # Extract domain from email
            domain = email.split('@')[-1]
            
            # Perform MX record lookup
            dns.resolver.resolve(domain, 'MX')
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            self.logger.warning(f"No MX records found for domain: {domain}")
            return False
        except Exception as e:
            self.logger.error(f"Domain validation error: {e}")
            return False

    def verify_email_existence(self, email: str) -> Dict:
        """
        Use Hunter.io to verify email existence
        
        :param email: Email to verify
        :return: Verification results
        """
        try:
            hunter_api_key = os.getenv('HUNTER_IO_API_KEY')
            if not hunter_api_key:
                self.logger.warning("Hunter.io API key not found")
                return {"status": "unknown"}
            
            params = {
                'email': email,
                'api_key': hunter_api_key
            }
            
            response = requests.get('https://api.hunter.io/v2/email-verifier', params=params)
            result = response.json()
            
            return {
                "status": result.get('data', {}).get('status', 'unknown'),
                "score": result.get('data', {}).get('score', 0)
            }
        
        except Exception as e:
            self.logger.error(f"Email verification error: {e}")
            return {"status": "error"}

    def advanced_email_verification(self, email: str) -> Dict:
        """
        Comprehensive email verification process
        
        :param email: Email address to verify
        :return: Verification results dictionary
        """
        # 1. Regex format check
        if not self.validate_email_format(email):
            return {
                'status': 'Invalid', 
                'reason': 'Format Error',
                'details': 'Email does not match standard format'
            }
    
        # 2. Domain validation
        if not self.validate_domain(email):
            return {
                'status': 'Invalid', 
                'reason': 'Domain Error',
                'details': 'Domain does not have valid MX records'
            }
    
        # 3. API-based verification (Hunter.io)
        try:
            api_result = self.verify_email_existence(email)
            
            # Combine verification results
            verification = {
                'status': api_result.get('status', 'Unknown'),
                'score': api_result.get('score', 0),
                'format_valid': True,
                'domain_valid': True
            }
            
            return verification
        
        except Exception as e:
            self.logger.error(f"Comprehensive email verification failed: {e}")
            return {
                'status': 'Error',
                'reason': 'Verification process failed',
                'details': str(e)
            }