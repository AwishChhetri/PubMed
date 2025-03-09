import pytest
from get_papers_list.fetch_papers import fetch_papers

def test_fetch_papers():
    # Test with a valid query
    papers = fetch_papers("machine learning", retmax=5)
    assert isinstance(papers, list)
    assert len(papers) <= 5

    # Test with an invalid query
    papers = fetch_papers("invalid_query_12345")
    assert isinstance(papers, list)
    assert len(papers) == 0