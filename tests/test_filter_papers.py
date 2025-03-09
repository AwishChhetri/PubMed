import pytest
from get_papers_list.filter_papers import filter_papers

def test_filter_papers():
    # Mock data for testing
    papers = [
        {
            "id": "12345",
            "title": "Test Paper 1",
            "date": "2023",
            "journal": "Test Journal",
            "doi": "10.1234/test.12345",
            "authors": [
                {
                    "name": "John Doe",
                    "affiliation": "Pharmaceutical Company Inc.",
                    "email": "john.doe@example.com"
                },
                {
                    "name": "Jane Smith",
                    "affiliation": "University of Test",
                    "email": "jane.smith@example.com"
                }
            ]
        }
    ]

    # Test filtering
    filtered_papers = filter_papers(papers)
    assert isinstance(filtered_papers, list)
    assert len(filtered_papers) == 1
    assert filtered_papers[0]["non_academic_authors"][0]["name"] == "John Doe"