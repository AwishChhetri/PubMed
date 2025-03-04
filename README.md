# PubMed Paper Filtering and Analysis Report

## 1. Approach
This script automates the retrieval, filtering, and analysis of research papers from PubMed based on a specified topic. The objective is to extract papers with at least one non-academic author, categorize them, and save the results to a CSV file for further analysis.

## 2. Methodology

### 2.1 Fetching Papers
- **Function:** `fetch_papers(topic: str, retmax: int = 200)`
- **Process:**
  - Calls PubMed's Entrez API (`esearch.fcgi`) to retrieve up to `retmax` paper IDs matching the given topic.
  - Parses the XML response to extract paper IDs.
  - Returns a list of dictionaries containing paper IDs.

### 2.2 Fetching Paper Details
- **Function:** `fetch_paper_details(paper_id: str)`
- **Process:**
  - Calls PubMed's `efetch.fcgi` API to get details for a given paper ID.
  - Extracts key information including:
    - Title
    - Journal
    - Publication Date
    - DOI
    - Author details (names, affiliations, and emails if available)
  - Returns a dictionary with extracted details.

### 2.3 Filtering Papers
- **Function:** `filter_papers(papers: List[Dict[str, Any]])`
- **Process:**
  - Retrieves detailed information for each paper using `fetch_paper_details` via multithreading (`ThreadPoolExecutor`).
  - Authors are categorized as **academic** or **non-academic** based on affiliation keywords (e.g., university, institute vs. company, corporation).
  - Extracts company names from non-academic authors using `extract_company_name()`.
  - Papers with at least one non-academic author are retained.

### 2.4 Saving Results to CSV
- **Function:** `save_to_csv(papers: List[Dict[str, Any]], filename: str)`
- **Process:**
  - Formats the filtered data into a structured pandas DataFrame.
  - Saves relevant fields, including paper ID, title, journal, publication date, DOI, non-academic authors, company names, and emails.
  - Outputs a CSV file with the filtered results.

## 3. Results
- The script successfully identifies and categorizes research papers based on author affiliations.
- Extracted and saved relevant data from PubMed, ensuring accurate filtering of non-academic authors.
- The final CSV file contains detailed information about selected papers, enabling further analysis of industry involvement in research.

## 4. Workflow Diagram
Below is a simplified workflow diagram of the approach:

```
                +----------------+
                |  User Input    |
                +----------------+
                        |
                        v
                +----------------+
                |  Fetch Papers  |
                +----------------+
                        |
                        v
                +----------------------+
                |  Fetch Paper Details |
                +----------------------+
                        |
                        v
                +----------------+
                |  Filter Papers |
                +----------------+
                        |
                        v
                +----------------+
                |  Save to CSV   |
                +----------------+
```

## 5. Conclusion
This automated approach efficiently identifies non-academic contributions to research. The filtering logic ensures that only papers with at least one industry-affiliated author are considered, making the dataset highly relevant for analyzing corporate participation in scientific publications.

## 6. Code Snippets

### Fetching Papers
```python
import requests
from Bio import Entrez

def fetch_papers(topic: str, retmax: int = 200):
    Entrez.email = "your_email@example.com"
    handle = Entrez.esearch(db="pubmed", term=topic, retmax=retmax)
    record = Entrez.read(handle)
    return record["IdList"]
```

### Fetching Paper Details
```python
def fetch_paper_details(paper_id: str):
    handle = Entrez.efetch(db="pubmed", id=paper_id, retmode="xml")
    return parse_xml(handle.read())
```

### Filtering Papers
```python
def filter_papers(papers):
    filtered = []
    for paper in papers:
        if any("Company" in aff for aff in paper["authors_affiliations"]):
            filtered.append(paper)
    return filtered
```

### Saving to CSV
```python
import pandas as pd

def save_to_csv(papers, filename):
    df = pd.DataFrame(papers)
    df.to_csv(filename, index=False)
```

---


