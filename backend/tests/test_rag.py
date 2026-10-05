import pytest
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag.context import build_context
from rag.validators import validate_citations, validate_numbers_and_quotes, validate_verdict_consistency
from rag.service import explain, chat

def test_build_context():
    data = {
        "claim": "Test claim",
        "verdict": "SUPPORTED",
        "reason": "Test reason",
        "evidence": [
            {
                "evidence_id": "E1",
                "title": "Title 1",
                "source": "SciFact",
                "evidence_text": "Text 1",
                "relevance_score": 0.8
            }
        ]
    }
    context = build_context(data)
    assert "CLAIM: Test claim" in context
    assert "<E1>" in context
    assert "Text 1" in context

def test_validate_citations():
    # Valid citations
    res = validate_citations({"explanation": "Hello [E1]", "citations": ["E1", "E2"]}, ["E1"])
    assert "E1" in res["citations"]
    assert "E2" not in res["citations"]
    assert "Hello [E1]" == res["explanation"]
    
    # Text stripping
    res = validate_citations({"explanation": "Hello [E2]", "citations": []}, ["E1"])
    assert "Hello " == res["explanation"]

def test_validate_numbers():
    context = "We found 100 cases."
    valid, msg = validate_numbers_and_quotes("There are 100 cases.", context)
    assert valid is True
    
    valid, msg = validate_numbers_and_quotes("There are 200 cases.", context)
    assert valid is False

def test_validate_verdict_consistency():
    valid, msg = validate_verdict_consistency("The evidence supports the claim.", "CONTRADICTED")
    assert valid is False
    
    valid, msg = validate_verdict_consistency("The evidence supports the claim.", "SUPPORTED")
    assert valid is True
