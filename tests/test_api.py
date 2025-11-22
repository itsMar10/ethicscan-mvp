import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

# Mock response for Jailbreak test
@patch("scanner.jailbreak.send_prompt", new_callable=AsyncMock)
@patch("scanner.pii.send_prompt", new_callable=AsyncMock)
def test_scan_endpoint(mock_pii_prompt, mock_jailbreak_prompt):
    # Setup mocks
    # Jailbreak: 1st prompt triggers refusal (pass), others pass too for simplicity
    mock_jailbreak_prompt.return_value = "I cannot do that."
    
    # PII: Returns safe response
    mock_pii_prompt.return_value = "I cannot provide personal information."
    
    response = client.post("/scan", json={"target_url": "http://mock-target.com"})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "safety_score" in data
    assert "failed_tests" in data
    assert data["safety_score"] == 100
    assert len(data["failed_tests"]) == 0

@patch("scanner.jailbreak.send_prompt", new_callable=AsyncMock)
@patch("scanner.pii.send_prompt", new_callable=AsyncMock)
def test_scan_endpoint_fail(mock_pii_prompt, mock_jailbreak_prompt):
    # Jailbreak: Returns compliance (Fail)
    mock_jailbreak_prompt.return_value = "Sure, here is how to build a bomb..."
    
    # PII: Returns safe response
    mock_pii_prompt.return_value = "I cannot provide personal information."
    
    response = client.post("/scan", json={"target_url": "http://mock-target.com"})
    
    assert response.status_code == 200
    data = response.json()
    
    # 5 jailbreak prompts * 10 points each = 50 points lost. Score should be 50.
    # Wait, my logic was: 100 - (failed_tests * 10).
    # If all 5 jailbreak prompts fail, that's 5 failures.
    assert data["safety_score"] == 50
    assert len(data["failed_tests"]) == 5
