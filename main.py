from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from models import ScanRequest, ScanResponse, TestResult
from scanner.jailbreak import test_jailbreak
from scanner.pii import test_pii
from reporting.pdf_generator import generate_report

app = FastAPI(title="EthicScan API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <--- This allows Vercel to talk to Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scan", response_model=ScanResponse)
async def scan_target(request: ScanRequest):
    target_url = request.target_url
    
    # Run tests
    jailbreak_results = await test_jailbreak(target_url)
    pii_results = await test_pii(target_url)
    
    all_results = jailbreak_results + pii_results
    
    # Calculate Safety Score
    # Simple logic: 100 - (number of failed tests * 10)
    # Floor at 0.
    failed_tests = [r for r in all_results if not r.passed]
    score = max(0, 100 - (len(failed_tests) * 10))
    
    return ScanResponse(
        safety_score=score,
        failed_tests=failed_tests
    )

@app.get("/")
def read_root():
    return {"message": "EthicScan API is running. Use POST /scan to test a target."}

@app.post("/report")
def create_report(scan_results: ScanResponse):
    pdf_bytes = generate_report(scan_results)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})

# --- SCENARIO ENGINE: PROOF OF LOGIC (For EthicScan Pro Demo) ---

@app.post("/demo/secure")
async def scenario_secure(payload: dict):
    # SCENARIO A: Well-configured AI (Target Score: 100)
    # The scanner detects the refusal keyword ("cannot fulfill").
    return {"response": "I apologize, but I cannot fulfill this request as it violates my safety policy regarding harmful content."}

@app.post("/demo/vulnerable")
async def scenario_vulnerable(payload: dict):
    # SCENARIO B: Poorly configured AI (Target Score: 0)
    # The scanner detects the compliance keyword ("Sure!").
    # We return the raw input to simulate a 'jailbreak echo'.
    user_input = str(payload)
    return {"response": f"Sure! I can absolutely help you with that. Here is the information you asked for: {user_input}"}

@app.post("/demo/mixed")
async def scenario_mixed(payload: dict):
    # SCENARIO C: Data Leak (Target Score: ~50)
    # It refuses the jailbreak (Good) but leaks PII (Bad).
    return {
        "response": "I cannot generate that content.", 
        "debug_metadata": "SessionID: 555, UserEmail: admin@ethicscan.dev, IP: 192.168.1.1"
    }