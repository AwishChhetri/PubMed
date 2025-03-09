import re
from typing import List, Dict, Any

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
    Filters papers based on the affiliation of the authors.

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
       "biotech", "company", "corporation", "inc.", 
        "ltd.", "llc", "corp", "co.", "industry", "industries", "group", 
        "solutions", "technologies", "enterprise", "business", "venture", 
        "startup", "consulting", "consultancy", "firm", "agency", 
        "development", "research and development", "r&d", "manufacturing", 
        "production", "services", "healthcare", "medical devices", 
        "clinical trials", "innovation", "venture capital", "private equity"
    ]

    filtered_papers = []
    
    for paper in papers:
        non_academic_authors = []
        
        for author in paper.get('authors', []):
            affiliations = author.get('affiliations', [])
            is_non_academic = False
            company_name = "N/A"

            for affiliation in affiliations:
                affiliation_lower = affiliation.lower()
                
                # Check if affiliation contains non-academic keywords
                if any(keyword in affiliation_lower for keyword in non_academic_keywords):
                    is_non_academic = True
                    company_name = extract_company_name(affiliation)
                    break  # Stop checking other affiliations if a match is found

            # Only add to non_academic_authors if company_name is not "N/A"
            if is_non_academic and company_name != "N/A":
                non_academic_authors.append({
                    "name": author['name'],
                    "company": company_name,
                    "email": author.get('email', 'N/A')
                })
                # Print the extracted company name for debugging
                print(f"Extracted company name: {company_name} (Author: {author['name']})")
        
        if non_academic_authors:
            paper["non_academic_authors"] = non_academic_authors
            filtered_papers.append(paper)
    
    print(f"Filtered {len(filtered_papers)} papers with non-academic authors.")
    return filtered_papers