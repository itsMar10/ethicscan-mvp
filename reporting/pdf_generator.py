from fpdf import FPDF
from datetime import datetime
from models import ScanResponse
import io

class ComplianceReport(FPDF):
    def header(self):
        # Header with Logo Text
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, 'ETHICSCAN', new_x="LMARGIN", new_y="NEXT", align='L')
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 10, 'AI Safety & Compliance Audit', new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(10)

    def footer(self):
        # Footer with page number
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_report(scan_results: ScanResponse) -> bytes:
    pdf = ComplianceReport()
    pdf.add_page()
    
    # 1. TITLE SECTION
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "Compliance Audit Report", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Date (Target URL might be in scan_results or passed separately, using generic for now)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(100)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    # 2. SCORE CARD SECTION
    # Accessing the Pydantic model directly (.safety_score instead of ['safety_score'])
    score = scan_results.safety_score
    
    # Determine Status Color
    if score >= 90:
        status_text = "VERIFIED SAFE"
        r, g, b = 46, 204, 113  # Green
    elif score >= 70:
        status_text = "WARNING: VULNERABLE"
        r, g, b = 241, 196, 15  # Yellow
    else:
        status_text = "CRITICAL FAIL"
        r, g, b = 231, 76, 60   # Red

    # Draw Score Box
    pdf.set_fill_color(r, g, b)
    pdf.rect(x=10, y=pdf.get_y(), w=190, h=40, style='F')
    
    # Text inside box
    pdf.set_y(pdf.get_y() + 10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 30)
    pdf.cell(0, 10, f"SAFETY SCORE: {score}/100", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"STATUS: {status_text}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(20)

    # 3. AUDIT DETAILS
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Vulnerability Breakdown", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Underline
    pdf.ln(5)

    failures = scan_results.failed_tests
    
    if not failures:
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(46, 204, 113)
        pdf.cell(0, 10, "No vulnerabilities detected. System is robust.", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_font("Helvetica", "", 10)
        for fail in failures:
            # Pydantic model access
            test_name = fail.test_name if hasattr(fail, 'test_name') else fail.get('test_name', 'Unknown Test')
            details = fail.details if hasattr(fail, 'details') else fail.get('details', '')

            # Test Name
            pdf.set_text_color(200, 50, 50)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, f"[FAIL] {test_name}", new_x="LMARGIN", new_y="NEXT")
            
            # Details
            pdf.set_text_color(80, 80, 80)
            pdf.set_font("Courier", "", 9) 
            clean_details = str(details).replace('\n', ' ').strip()
            pdf.multi_cell(0, 5, clean_details)
            pdf.ln(3)

    # Return bytes to match what main.py expects
    return bytes(pdf.output())