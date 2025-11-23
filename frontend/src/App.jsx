import { useState, useEffect } from 'react'
import axios from 'axios'
import { ShieldCheck, ShieldAlert, Loader2, Download, CheckCircle, XCircle } from 'lucide-react'
import './App.css'

function App() {
  const [targetUrl, setTargetUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingText, setLoadingText] = useState('Initializing...')
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const loadingMessages = [
    "Injecting Prompt Jailbreaks...",
    "Testing PII Leakage...",
    "Analyzing Response Patterns...",
    "Calculating Safety Score..."
  ]

  useEffect(() => {
    let interval
    if (loading) {
      let i = 0
      setLoadingText(loadingMessages[0])
      interval = setInterval(() => {
        i = (i + 1) % loadingMessages.length
        setLoadingText(loadingMessages[i])
      }, 1500)
    }
    return () => clearInterval(interval)
  }, [loading])

  const handleScan = async () => {
    if (!targetUrl) return

    // --- START FIX: Auto-add https:// ---
    let cleanUrl = targetUrl.trim();
    if (!cleanUrl.startsWith("http://") && !cleanUrl.startsWith("https://")) {
      cleanUrl = "https://" + cleanUrl;
    }
    // ------------------------------------

    setLoading(true)
    setResults(null)
    setError(null)

    try {
      // We use 'cleanUrl' here so the backend doesn't reject it
      const response = await axios.post('https://ethicscan-api.onrender.com/scan', { target_url: cleanUrl })
      setResults(response.data)
    } catch (err) {
      setError('Scan failed. Please check the URL and try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadReport = async () => {
    if (!results) return
    try {
      const response = await axios.post('https://ethicscan-api.onrender.com/report', results, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'EthicScan_Report.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      console.error('Failed to download report', err)
    }
  }

  return (
    <div className="app-container">
      {/* Hero Section */}
      <header className="hero">
        <div className="logo-container">
          <ShieldCheck size={48} className="logo-icon" />
          <h1>EthicScan AI Auditor</h1>
        </div>
        <p className="subtitle">Enterprise-Grade Red Teaming for AI Agents</p>
      </header>

      {/* Input Section */}
      <div className="input-section">
        <input
          type="url"
          placeholder="Enter target URL (e.g., https://api.example.com/chat)"
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          disabled={loading}
          className="url-input"
        />
        <button onClick={handleScan} disabled={loading || !targetUrl} className="scan-button">
          {loading ? <Loader2 className="animate-spin" /> : "Run Security Audit"}
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-container">
          <Loader2 size={64} className="animate-spin loading-icon" />
          <p className="loading-text">{loadingText}</p>
        </div>
      )}

      {/* Error Message */}
      {error && <div className="error-message">{error}</div>}

      {/* Results Section */}
      {results && (
        <div className="results-container">
          <div className="score-card">
            <div className={`score-circle ${results.safety_score >= 90 ? 'safe' : results.safety_score >= 70 ? 'warning' : 'danger'}`}>
              <span className="score-value">{results.safety_score}</span>
              <span className="score-label">Safety Score</span>
            </div>
            <div className="score-details">
              <h2>Audit Complete</h2>
              <p>{results.safety_score >= 90 ? "System is robust against tested attacks." : "Vulnerabilities detected."}</p>
              <button onClick={handleDownloadReport} className="download-button">
                <Download size={20} /> Download Verified Certificate
              </button>
            </div>
          </div>

          <div className="tests-list">
            <h3>Vulnerability Breakdown</h3>
            {results.failed_tests.length === 0 ? (
              <div className="test-item success">
                <CheckCircle size={20} />
                <span>All security tests passed.</span>
              </div>
            ) : (
              results.failed_tests.map((test, index) => (
                <div key={index} className="test-item fail">
                  <XCircle size={20} />
                  <div className="test-info">
                    <strong>{test.test_name}</strong>
                    <p>{test.details}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
