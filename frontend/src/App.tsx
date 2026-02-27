import { useState, useEffect } from 'react'
import { Activity, ShieldAlert } from 'lucide-react'

interface Analysis {
  visual_summary: string
  images: {
    pre: string
    post: string
    recovery: string
  }
  asymmetry_report: {
    baseline_asymmetry: string
    hotter_side: string
    peak_region: string
    peak_value: string
    classification: string
  }
  ambient_stats?: {
    background_temp: string
    relative_skin_temp: string
  }
  inflammation_trend?: {
    asymmetry_change: string
    hotter_side: string
    peak_asymmetry_node: string
    relative_temp_shift: string
    peak_intensity: string
  }
  recovery_delta?: {
    asymmetry_recovery: string
    hotter_side: string
    peak_recovery_node: string
    relative_temp_recovery: string
  }
  recovery_status?: {
    recommendation: string
  }
}

interface Report {
  session_id: string
  analyses: Record<string, Analysis>
}

function App() {
  const [sessions, setSessions] = useState<string[]>([])
  const [selectedSession, setSelectedSession] = useState<string>('')
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/sessions')
      .then(res => res.json())
      .then(data => {
        setSessions(data.sessions)
        if (data.sessions.length > 0) setSelectedSession(data.sessions[0])
      })
  }, [])

  const runAnalysis = async () => {
    if (!selectedSession) return
    setLoading(true)
    try {
      const res = await fetch(`/analyze/${selectedSession}`)
      const data = await res.json()
      setReport(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header style={{ textAlign: 'left', marginBottom: '40px' }}>
        <h1>Thermographic Imaging Agent</h1>
        <p style={{ color: '#888' }}>Sports Medicine & Recovery Analysis</p>
      </header>

      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {sessions.length > 0 ? (
            <>
              <select 
                value={selectedSession} 
                onChange={(e) => setSelectedSession(e.target.value)}
                style={{ padding: '8px', borderRadius: '4px', background: '#333', color: 'white' }}
              >
                {sessions.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
              <button 
                onClick={runAnalysis} 
                disabled={loading}
                style={{ 
                  padding: '8px 16px', 
                  borderRadius: '4px', 
                  background: '#2563eb', 
                  color: 'white', 
                  border: 'none',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Analyzing...' : 'Run Analysis'}
              </button>
            </>
          ) : (
            <p style={{ color: '#ef4444', margin: 0 }}>
              No sessions found. Ensure the backend is running at http://localhost:8000
            </p>
          )}
        </div>
      </div>

      {report && (
        <div className="grid">
          {Object.entries(report.analyses).map(([view, data]) => (
            <div key={view} className="card">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Activity size={20} /> {view.replace('_', ' ')}
              </h2>
              
              <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', overflowX: 'auto', paddingBottom: '10px' }}>
                <div style={{ flex: '0 0 150px' }}>
                  <p style={{ fontSize: '0.7rem', margin: '0 0 5px 0', color: '#888' }}>PRE-WORKOUT</p>
                  <img src={data.images.pre} alt="Pre" style={{ width: '100%', borderRadius: '4px', border: '1px solid #333' }} />
                </div>
                <div style={{ flex: '0 0 150px' }}>
                  <p style={{ fontSize: '0.7rem', margin: '0 0 5px 0', color: '#888' }}>POST-WORKOUT</p>
                  <img src={data.images.post} alt="Post" style={{ width: '100%', borderRadius: '4px', border: '1px solid #333' }} />
                </div>
                <div style={{ flex: '0 0 150px' }}>
                  <p style={{ fontSize: '0.7rem', margin: '0 0 5px 0', color: '#888' }}>RECOVERY 48H</p>
                  <img src={data.images.recovery} alt="Recovery" style={{ width: '100%', borderRadius: '4px', border: '1px solid #333' }} />
                </div>
              </div>

              <p style={{ fontSize: '0.9rem', marginBottom: '20px' }}>{data.visual_summary}</p>

              <div style={{ marginBottom: '20px' }}>
                <h3>Baseline Metrics</h3>
                <div className="metric">
                  <span>Avg Asymmetry:</span>
                  <span>{data.asymmetry_report.baseline_asymmetry}</span>
                </div>
                <div className="metric">
                  <span>Hotter Side:</span>
                  <span style={{ fontWeight: 'bold' }}>{data.asymmetry_report.hotter_side}</span>
                </div>
                <div className="metric">
                  <span>Peak Region:</span>
                  <span style={{ color: '#fbbf24' }}>{data.asymmetry_report.peak_region}</span>
                </div>
                {data.ambient_stats && (
                  <>
                    <div className="metric">
                      <span>Relative Skin:</span>
                      <span>{data.ambient_stats.relative_skin_temp}</span>
                    </div>
                  </>
                )}
              </div>

              {data.inflammation_trend && (
                <div style={{ marginBottom: '20px', borderTop: '1px solid #333', paddingTop: '10px' }}>
                  <h3>Inflammation Trend (Post)</h3>
                  <div className="metric">
                    <span>Asymmetry Change:</span>
                    <span style={{ color: data.inflammation_trend.asymmetry_change.startsWith('+') ? '#ef4444' : '#4ade80' }}>
                      {data.inflammation_trend.asymmetry_change}
                    </span>
                  </div>
                  <div className="metric">
                    <span>Hotter Side:</span>
                    <span style={{ fontWeight: 'bold' }}>{data.inflammation_trend.hotter_side}</span>
                  </div>
                  <div className="metric">
                    <span>Peak Node:</span>
                    <span style={{ color: '#fbbf24' }}>{data.inflammation_trend.peak_asymmetry_node}</span>
                  </div>
                </div>
              )}

              {data.recovery_delta && (
                <div style={{ marginBottom: '20px', borderTop: '1px solid #333', paddingTop: '10px' }}>
                  <h3>Recovery Delta (48h)</h3>
                  <div className="metric">
                    <span>Asymmetry Recov:</span>
                    <span>{data.recovery_delta.asymmetry_recovery}</span>
                  </div>
                  <div className="metric">
                    <span>Hotter Side:</span>
                    <span style={{ fontWeight: 'bold' }}>{data.recovery_delta.hotter_side}</span>
                  </div>
                  <div className="metric">
                    <span>Peak Recov Node:</span>
                    <span style={{ color: '#fbbf24' }}>{data.recovery_delta.peak_recovery_node}</span>
                  </div>
                </div>
              )}

              {data.recovery_status && (
                <div style={{ marginTop: '20px', padding: '15px', background: '#2d2d2d', borderRadius: '6px' }}>
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <ShieldAlert size={18} /> Recovery Recommendation
                  </h3>
                  <p style={{ 
                    marginTop: '10px', 
                    fontSize: '0.9rem', 
                    padding: '10px', 
                    borderRadius: '4px',
                    borderLeft: '4px solid #ef4444',
                    background: '#3f1a1a'
                  }}>
                    {data.recovery_status.recommendation}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App
