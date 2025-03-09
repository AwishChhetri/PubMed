# Get Papers List

A Python program to fetch research papers from PubMed based on a user-specified query. The program identifies papers with at least one author affiliated with a pharmaceutical or biotech company and returns the results as a CSV file.

---

## **Features**
- Fetches research papers from PubMed using the PubMed API.
- Filters papers based on author affiliations to identify non-academic authors (e.g., pharmaceutical or biotech companies).
- Saves the results to a CSV file with the following columns:
  - **PubmedID**: Unique identifier for the paper.
  - **Title**: Title of the paper.
  - **Publication Date**: Date the paper was published.
  - **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions.
  - **Company Affiliation(s)**: Names of pharmaceutical/biotech companies.
  - **Corresponding Author Email**: Email address of the corresponding author.
- Supports PubMed's full query syntax for flexibility.
- Command-line interface with options for specifying the output file and enabling debug mode.

---

## **Installation**

### **Prerequisites**
- Python 3.8 or higher.
- [Poetry](https://python-poetry.org/) for dependency management.

### **Steps**
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/get-papers-list.git
   cd get-papers-list
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

---

## **Usage**

### **Command-Line Arguments**
- **Query**: The PubMed search query (required).
- **-f, --file**: Specify the filename to save the results as a CSV file. If not provided, the results will be printed to the console.
- **-d, --debug**: Enable debug mode to print detailed information during execution.

### **Examples**
1. Fetch papers for the query "Health Care with Machine learning" and save the results to `output.csv`:
   ```bash
   poetry run get-papers-list "Health Care with Machine learning" -f output.csv
   ```

2. Fetch papers for the query "Cancer treatment" and print the results to the console:
   ```bash
   poetry run get-papers-list "Cancer treatment"
   ```

3. Fetch papers for the query "Diabetes research" with debug mode enabled:
   ```bash
   poetry run get-papers-list "Diabetes research" -d
   ```

---

## **Code Organization**

The project is organized into the following modules:

### **1. `get_papers_list/fetch_papers.py`**
- Fetches a list of paper IDs from PubMed based on a query.
- Uses the PubMed `esearch` API.

### **2. `get_papers_list/filter_papers.py`**
- Filters papers based on author affiliations to identify non-academic authors.
- Uses heuristics to detect pharmaceutical or biotech companies.

### **3. `get_papers_list/utils.py`**
- Contains utility functions, including `fetch_paper_details`, which fetches detailed information for a specific paper using its PubMed ID.

### **4. `get_papers_list_cli.py`**
- The command-line interface (CLI) script that ties everything together.
- Calls `fetch_papers`, `fetch_paper_details`, and `filter_papers` to fetch, filter, and save the results.

---

## **Testing**

### **Unit Tests**
Unit tests are located in the `tests/` directory. To run the tests, use the following command:

```bash
poetry run pytest
```

### **Test Coverage**
To measure test coverage, install the `pytest-cov` plugin and run:

```bash
poetry run pytest --cov=get_papers_list
```

### **Example Test Cases**
1. **Test `fetch_papers`**:
   - Verify that the function returns a list of paper IDs for a valid query.
   - Verify that the function handles invalid queries gracefully.

2. **Test `fetch_paper_details`**:
   - Verify that the function fetches detailed information for a valid PubMed ID.
   - Verify that the function handles invalid PubMed IDs gracefully.

3. **Test `filter_papers`**:
   - Verify that the function correctly identifies non-academic authors.
   - Verify that the function handles papers with no non-academic authors gracefully.

---

## **Tools and Libraries Used**
- **PubMed API**: Used to fetch papers and their details.
  - [PubMed API Documentation](https://pubmed.ncbi.nlm.nih.gov/help/)
- **Python Libraries**:
  - `requests`: For making HTTP requests to the PubMed API.
  - `pandas`: For saving the results to a CSV file.
  - `argparse`: For handling command-line arguments.
  - `concurrent.futures`: For concurrent API calls to improve performance.
- **Poetry**: For dependency management and packaging.
  - [Poetry Documentation](https://python-poetry.org/docs/)

---

## **Publishing to TestPyPI**

The module can be published to TestPyPI for distribution. Follow these steps:

1. Build the package:
   ```bash
   poetry build
   ```

2. Publish to TestPyPI:
   ```bash
   poetry publish -r test-pypi
   ```

3. Install the module from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ get-papers-list
   ```

---

## **Contributing**

Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Contact**

For questions or feedback, please contact:
- **Your Name**: your.email@example.com
- **GitHub**: [your-username](https://github.com/your-username)

---

## **Example Output**

### **CSV Output**
If you save the results to a CSV file, it will look like this:

| PubmedID  | Title                                                                 | Publication Date | Non-academic Author(s)       | Company Affiliation(s) | Corresponding Author Email         |
|-----------|-----------------------------------------------------------------------|------------------|------------------------------|------------------------|------------------------------------|
| 40057810  | Maternal epigenetic index links early neglect to later neglectful... | 2025             | Silvia Herrero-Roldán        | UNIE Universidad       | silvia.herrero@universidadunie.com |

---

### **Console Output**
If you print the results to the console, it will look like this:

```plaintext
Found 10 papers.
Extracted company name: UNIE Universidad (Author: Silvia Herrero-Roldán)
Filtered 1 papers with non-academic authors.
{
    "id": "40057810",
    "title": "Maternal epigenetic index links early neglect to later neglectful care and other psychopathological, cognitive, and bonding effects.",
    "date": "2025",
    "journal": "Clinical epigenetics",
    "doi": "10.1186/s13148-025-01839-7",
    "non_academic_authors": [
        {
            "name": "Silvia Herrero-Roldán",
            "company": "UNIE Universidad",
            "email": "silvia.herrero@universidadunie.com"
        }
    ]
}
```

