# tests/test_fetch_papers.py
import pytest
from get_papers_list.fetch_papers import fetch_papers

def test_fetch_papers():
    papers = fetch_papers("machine learning", retmax=10)
    assert isinstance(papers, list)
    assert len(papers) <= 10