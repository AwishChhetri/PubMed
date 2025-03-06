import requests
import pandas as pd
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

def fetch_papers(topic: str, retmax: int = 300) -> List[Dict[str, Any]]:
    """
    Fetches a list of paper IDs related to the given topic from PubMed.

    Args:
        topic (str): The search topic for fetching papers.
        retmax (int): Maximum number of papers to fetch. Default is 200.

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

def fetch_paper_details(paper_id: str) -> Dict[str, Any]:
    """
    Fetches detailed information for a specific paper using its PubMed ID.

    Args:
        paper_id (str): The PubMed ID of the paper.

    Returns:
        Dict[str, Any]: A dictionary containing paper details such as title, date, journal, DOI, and authors.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": paper_id, "retmode": "xml"}
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        title = root.find(".//ArticleTitle")
        pub_date = root.find(".//PubDate/Year")
        journal = root.find(".//Journal/Title")
        doi = root.find(".//ELocationID[@EIdType='doi']")
        
        title = title.text if title is not None else "N/A"
        pub_date = pub_date.text if pub_date is not None else "N/A"
        journal = journal.text if journal is not None else "N/A"
        doi = doi.text if doi is not None else "N/A"
        
        authors = []
        for author in root.findall(".//Author"):
            fore_name = author.find("ForeName")
            last_name = author.find("LastName")
            affiliation = author.find(".//Affiliation")
            email = None

            if affiliation is not None:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', affiliation.text)
                if email_match:
                    email = email_match.group(0)

            authors.append({
                "name": f"{fore_name.text if fore_name is not None else ''} {last_name.text if last_name is not None else ''}".strip(),
                "affiliation": affiliation.text if affiliation is not None else "",
                "email": email if email else "N/A"
            })
        
        return {"id": paper_id, "title": title, "date": pub_date, "journal": journal, "doi": doi, "authors": authors}
    except requests.RequestException as e:
        print(f"Failed to fetch details for ID {paper_id}: {e}")
        return None

def extract_company_name(affiliation: str) -> str:
    """
    Extracts the company name from an author's affiliation string.

    Args:
        affiliation (str): The affiliation string of the author.

    Returns:
        str: The extracted company name or "N/A" if not found.
    """
    company_patterns = [
        r"\b(?:inc\.?|ltd\.?|llc\.?|corp\.?|corporation|company|co\.?)\b",
        r"\b(?:pharmaceuticals?|biotech|industries|solutions|group)\b",
    ]
    
    for part in affiliation.split(","):
        part = part.strip()
        for pattern in company_patterns:
            if re.search(pattern, part, re.IGNORECASE):
                return part
    return "N/A"

def filter_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filters papers based on the affiliation of the authors. Only papers with at least one non-academic author are included.

    Args:
        papers (List[Dict[str, Any]]): A list of papers to filter.

    Returns:
        List[Dict[str, Any]]: A list of filtered papers with non-academic authors.
    """
    academic_keywords = [
    "university", "college", "institute", "research center", "hospital", 
    "academy", "school", "faculty", "department", "laboratory", "clinic", 
    "medical center", "teaching hospital", "educational", "scholar", 
    "postgraduate", "undergraduate", "phd", "professor", "lecturer", 
    "researcher", "scientist", "academic", "higher education", "campus"
]

    non_academic_keywords = [
    "pharmaceutical", "biotech", "company", "corporation", "inc.", 
    "ltd.", "llc", "corp", "co.", "industry", "industries", "group", 
    "solutions", "technologies", "enterprise", "business", "venture", 
    "startup", "consulting", "consultancy", "firm", "agency", 
    "development", "research and development", "r&d", "manufacturing", 
    "production", "services", "healthcare", "medical devices", 
    "clinical trials", "innovation", "venture capital", "private equity"
]

    filtered_papers = []
    
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda p: fetch_paper_details(p["id"]), papers))
    
    for details in filter(None, results):
        academic_authors = []
        non_academic_authors = []
        
        for author in details.get('authors', []):
            affiliation = author.get('affiliation', '').lower()
            
            if any(keyword in affiliation for keyword in academic_keywords):
                academic_authors.append(author['name'])
            
            elif any(keyword in affiliation for keyword in non_academic_keywords):
                company_name = extract_company_name(author.get('affiliation', ''))
                non_academic_authors.append({
                    "name": author['name'],
                    "company": company_name
                })
        
        if len(non_academic_authors) > 0:
            details["academic_authors"] = academic_authors
            details["non_academic_authors"] = non_academic_authors
            filtered_papers.append(details)
    
    print(f"Filtered {len(filtered_papers)} papers with non-academic authors.")
    return filtered_papers

def save_to_csv(papers: List[Dict[str, Any]], filename: str) -> None:
    """
    Saves the filtered papers to a CSV file.

    Args:
        papers (List[Dict[str, Any]]): A list of filtered papers.
        filename (str): The name of the CSV file to save the data.
    """
    df = pd.DataFrame([
        {
            "PubmedID": p['id'],
            "Title": p['title'],
            "Journal": p['journal'],
            "Publication Date": p['date'],
            "DOI": p['doi'],
            "Non-academic Author(s)": ", ".join([a['name'] for a in p.get('non_academic_authors', [])]),
            "Company Name(s)": ", ".join([a['company'] for a in p.get('non_academic_authors', []) if a['company'] != "N/A"]),
            "Emails": ", ".join([a['email'] for a in p.get('authors', []) if a['email'] != "N/A" and a['name'] in [na['name'] for na in p.get('non_academic_authors', [])]])
        }
        for p in papers
    ])
    df.to_csv(filename, index=False)
    print(f"Saved {len(papers)} papers to {filename}.")

def main():
    """
    Main function to fetch, filter, and save papers related to a specific topic.
    """
    topic = "Health Care with Machine learning"
    print(f"Fetching papers for topic: {topic}...")
    papers = fetch_papers(topic)
    if not papers:
        print("No papers found. Exiting.")
        return
    
    print("Filtering papers based on author affiliation...")
    filtered_papers = filter_papers(papers)
    if not filtered_papers:
        print("No relevant papers found after filtering. Exiting.")
        return
    
    print("Saving filtered papers to CSV...")
    save_to_csv(filtered_papers, "filtered_papers.csv")
    print("Process completed.")

if __name__ == "__main__":
    main()