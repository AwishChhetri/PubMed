import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def fetch_papers(topic: str, retmax: int = 50) -> List[Dict[str, Any]]:
    """
    Fetches a list of paper IDs related to the given topic from PubMed.

    Args:
        topic (str): The search topic for fetching papers.
        retmax (int): Maximum number of papers to fetch. Default is 300.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing paper IDs.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": topic, "retmode": "xml", "retmax": retmax}
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        papers_list = [id_elem.text for id_elem in root.findall(".//Id")]
        
        if not papers_list:
            print("No papers found for the given topic.")
            return []
        
        print(f"Found {len(papers_list)} papers.")
        return [{"id": paper_id} for paper_id in papers_list]
    except requests.RequestException as e:
        print(f"Error fetching papers: {e}")
        return []