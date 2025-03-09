import requests
import xml.etree.ElementTree as ET
import re
import time
from typing import Dict, Any

def fetch_paper_details(paper_id: str, max_retries: int = 3, delay: float = 0.5) -> Dict[str, Any]:
    """
    Fetches detailed information for a specific paper using its PubMed ID.

    Args:
        paper_id (str): The PubMed ID of the paper.
        max_retries (int): Maximum number of retries for failed requests. Default is 3.
        delay (float): Delay between retries in seconds. Default is 0.5 seconds.

    Returns:
        Dict[str, Any]: A dictionary containing paper details such as title, date, journal, DOI, and authors.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": paper_id, "retmode": "xml"}
    
    for attempt in range(max_retries):
        try:
            # Fetch the paper details from PubMed
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status() 
            root = ET.fromstring(response.content)

            # Extract basic paper details
            title = root.findtext(".//ArticleTitle") or "N/A"
            pub_date = root.findtext(".//PubDate/Year") or "N/A"
            journal = root.findtext(".//Journal/Title") or "N/A"
            doi = root.findtext(".//ELocationID[@EIdType='doi']") or "N/A"

            # Extract authors and their affiliations
            authors = []
            for author in root.findall(".//Author"):
                fore_name = author.findtext("ForeName") or ""
                last_name = author.findtext("LastName") or ""
                affiliations = [aff.text for aff in author.findall(".//Affiliation") if aff.text]
                email = None

                # Extract email from affiliations (if present)
                for aff in affiliations:
                    if aff and "@" in aff:
                        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', aff)
                        if email_match:
                            email = email_match.group(0)
                            break

                authors.append({
                    "name": f"{fore_name} {last_name}".strip(),
                    "affiliations": affiliations,
                    "email": email if email else "N/A"
                })


            return {
                "id": paper_id,
                "title": title,
                "date": pub_date,
                "journal": journal,
                "doi": doi,
                "authors": authors
            }
        except requests.RequestException as e:
            if attempt < max_retries - 1:
             
                time.sleep(delay) 
                delay *= 2 
            else:
       
                return None