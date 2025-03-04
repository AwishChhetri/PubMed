import requests
import pandas as pd
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

def fetch_papers(topic: str, retmax: int = 200) -> List[Dict[str, Any]]:
    """
    Fetches papers from PubMed based on a given topic and processes them.
    """
    print(f"Fetching papers for topic: {topic}...")
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
        
        print(f"Found {len(papers_list)} papers. Fetching details...")
        return [{"id": paper_id} for paper_id in papers_list]
    except requests.RequestException as e:
        print(f"Error fetching papers: {e}")
        return []

def fetch_paper_details(paper_id: str) -> Dict[str, Any]:
    """
    Fetches details of a paper given its PubMed ID and extracts emails.
    """
    print(f"Fetching details for paper ID: {paper_id}...")
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

            # Extract email if it appears in Affiliation
            if affiliation is not None:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', affiliation.text)
                if email_match:
                    email = email_match.group(0)

            authors.append({
                "name": f"{fore_name.text if fore_name is not None else ''} {last_name.text if last_name is not None else ''}".strip(),
                "affiliation": affiliation.text if affiliation is not None else "",
                "email": email if email else "N/A"
            })
        
        print(f"Details fetched for paper ID: {paper_id}")
        print({"id": paper_id, "title": title, "date": pub_date, "journal": journal, "doi": doi, "authors": authors})
        
        return {"id": paper_id, "title": title, "date": pub_date, "journal": journal, "doi": doi, "authors": authors}
    except requests.RequestException as e:
        print(f"Failed to fetch details for ID {paper_id}: {e}")
        return None

def extract_company_name(affiliation: str) -> str:
    """
    Extracts the company name from an affiliation string.
    """
    # Common patterns for company names
    company_patterns = [
        r"\b(?:inc\.?|ltd\.?|llc\.?|corp\.?|corporation|company|co\.?)\b",
        r"\b(?:pharmaceuticals?|biotech|industries|solutions|group)\b",
    ]
    
    # Split the affiliation into parts and look for patterns
    for part in affiliation.split(","):
        part = part.strip()
        for pattern in company_patterns:
            if re.search(pattern, part, re.IGNORECASE):
                return part
    return "N/A"

def filter_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filters papers and categorizes authors as academic or non-academic.
    Only papers with at least one non-academic author are included.
    Extracts company names for non-academic authors.
    """
    print("Filtering papers based on author affiliation...")
    academic_keywords = ["university", "college", "institute", "research center", "hospital"]
    non_academic_keywords = ["pharmaceutical", "biotech", "company", "corporation"]
    
    filtered_papers = []
    
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda p: fetch_paper_details(p["id"]), papers))
    
    for details in filter(None, results):
        academic_authors = []
        non_academic_authors = []
        
        for author in details.get('authors', []):
            affiliation = author.get('affiliation', '').lower()
            
            # Check if the affiliation contains any academic keywords
            if any(keyword in affiliation for keyword in academic_keywords):
                academic_authors.append(author['name'])
            
            # Check if the affiliation contains any non-academic keywords
            elif any(keyword in affiliation for keyword in non_academic_keywords):
                company_name = extract_company_name(author.get('affiliation', ''))
                non_academic_authors.append({
                    "name": author['name'],
                    "company": company_name
                })
        
        # Only include papers with at least one non-academic author
        if len(non_academic_authors) > 0:
            details["academic_authors"] = academic_authors
            details["non_academic_authors"] = non_academic_authors
            filtered_papers.append(details)
    
    print(f"Filtering complete. {len(filtered_papers)} papers with non-academic authors processed.")
    return filtered_papers

def save_to_csv(papers: List[Dict[str, Any]], filename: str) -> None:
    """
    Saves non-academic authors' names, company names, and emails in a CSV file.
    """
    print("Saving filtered papers to CSV...")
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
    print("--------------------------------------------------------")
    print(df)
    df.to_csv(filename, index=False)
    print(f"Filtered papers saved to {filename}")

def main():
    topic = "Health Care Machine learning"
    papers = fetch_papers(topic)
    if not papers:
        print("No papers found. Exiting.")
        return
    
    filtered_papers = filter_papers(papers)
    if not filtered_papers:
        print("No relevant papers found after filtering. Exiting.")
        return
    
    save_to_csv(filtered_papers, "filtered_papers.csv")

if __name__ == "__main__":
    main()