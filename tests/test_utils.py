import pytest
from get_papers_list.utils import fetch_paper_details

def test_fetch_paper_details():
    # Test with a valid PubMed ID
    paper_details = fetch_paper_details("12345")
    assert isinstance(paper_details, dict)
    assert "id" in paper_details
    assert "title" in paper_details
    assert "authors" in paper_details

    # Test with an invalid PubMed ID
    paper_details = fetch_paper_details("invalid_id")
    assert paper_details is None