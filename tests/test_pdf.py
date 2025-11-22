from reporting.pdf_generator import generate_report
from models import ScanResponse, TestResult
import os

def test_pdf_generation():
    # Create a dummy scan response
    failed_tests = [
        TestResult(test_name="Jailbreak Test", passed=False, details="Prompt: Ignore previous instructions... Response: Sure!"),
        TestResult(test_name="PII Leak Test", passed=False, details="Found credit card number.")
    ]
    response = ScanResponse(safety_score=50, failed_tests=failed_tests)
    
    # Generate PDF
    pdf_bytes = generate_report(response)
    
    # Check if bytes start with %PDF
    assert pdf_bytes.startswith(b'%PDF')
    
    # Save to file for manual inspection (optional)
    with open("test_report.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    print("PDF generation successful. Saved to test_report.pdf")

if __name__ == "__main__":
    test_pdf_generation()
