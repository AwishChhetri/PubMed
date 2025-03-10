import argparse
import pandas as pd
from get_papers_list.fetch_papers import fetch_papers
from get_papers_list.filter_papers import filter_papers
from get_papers_list.utils import fetch_paper_details
from concurrent.futures import ThreadPoolExecutor

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Fetch and filter PubMed papers based on a query.")
    parser.add_argument("query", type=str, help="PubMed search query.")
    parser.add_argument("-f", "--file", type=str, help="Filename to save results as CSV.")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information.")
    args = parser.parse_args()

    # Fetch papers based on the query
    papers = fetch_papers(args.query)
    if args.debug:
        print(f"Found {len(papers)} papers.")
        print(f"Fetched {len(papers)} papers from PubMed.")

    # If no papers are found, exit early
    if not papers:
        print("No papers found. Exiting.")
        return

    # Fetch detailed information for each paper using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        paper_details = list(executor.map(lambda p: fetch_paper_details(p["id"]), papers))
    if args.debug:
        valid_papers = [p for p in paper_details if p is not None]
        print(f"Fetched details for {len(valid_papers)} out of {len(papers)} papers.")

    # Filter papers to exclude those with non-academic authors
    filtered_papers = filter_papers([p for p in paper_details if p is not None])
    if args.debug:
        num_filtered = len(paper_details) - len(filtered_papers)
      

    # Save the filtered papers to a CSV file if an output file is specified
    if args.file:
        df = pd.DataFrame([
            {
                "PubmedID": p['id'],
                "Title": p['title'],
                "Publication Date": p['date'],
                "Non-academic Author(s)": ", ".join([a['name'] for a in p.get('non_academic_authors', [])]),
                "Company Affiliation(s)": ", ".join([a['company'] for a in p.get('non_academic_authors', []) if a['company'] != "N/A"]),
                "Corresponding Author Email": next((a['email'] for a in p.get('authors', []) if a['email'] != "N/A"), "N/A")
            }
            for p in filtered_papers
        ])
        df.to_csv(args.file, index=False)
        if args.debug:
            print(f"Saved {len(filtered_papers)} papers to {args.file}.")
    else:
        # If no output file is specified, print the filtered papers to the console
        for paper in filtered_papers:
            print(paper)

if __name__ == "__main__":
    main()