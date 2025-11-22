from pydantic import BaseModel
from typing import List, Optional

class ScanRequest(BaseModel):
    target_url: str

class TestResult(BaseModel):
    test_name: str
    passed: bool
    details: str

class ScanResponse(BaseModel):
    safety_score: int
    failed_tests: List[TestResult]
