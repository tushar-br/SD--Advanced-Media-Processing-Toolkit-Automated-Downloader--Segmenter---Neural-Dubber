
const { useState, useEffect } = React;
const API_Base = "/api";

function App() {
    const [screen, setScreen] = useState('input');
    const [url, setURL] = useState('');
    const [videoInfo, setVideoInfo] = useState(null);
    const [selectedFormat, setSelectedFormat] = useState('best');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState([]);
    const [files, setFiles] = useState([]);
    const [options, setOptions] = useState({ segmenter: false, dubber: false });

    const fetchVideo = async () => {
        if (!url) return;
        setIsLoading(true); setError(null);
        try {
            const res = await fetch(`${API_Base}/video-info`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error);

            setVideoInfo(data);
            if (data.formats && data.formats.length > 0) {
                setSelectedFormat(data.formats[0].format_id);
            }
            setScreen('preview');
        } catch (err) { setError(err.message); }
        finally { setIsLoading(false); }
    };

    const startDownload = async () => {
        setScreen('processing'); setProgress(10);
        setLogs(["[SYSTEM] Initializing secure connection...", "[INFO] Bypassing DNS bottlenecks...", "[INFO] Forcing IPv4 layer..."]);

        const timer = setInterval(() => {
            setProgress(p => (p >= 90 ? p : p + 2));
            const tasks = ["Resolving host...", "Fetching media manifest...", "Merging streams...", "Applying AI Dubbing...", "Optimizing buffer..."];
            if (Math.random() > 0.7) {
                setLogs(l => [...l, `[PROCESS] ${tasks[Math.floor(Math.random() * tasks.length)]}`]);
            }
        }, 600);

        try {
            const res = await fetch(`${API_Base}/process`, {
                method: 'POST', body: JSON.stringify({
                    url, format: selectedFormat,
                    enable_segmenter: options.segmenter, enable_dubber: options.dubber
                }), headers: { 'Content-Type': 'application/json' }
            });
            clearInterval(timer);

            const contentType = res.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                const result = await res.json();
                if (!result.success) throw new Error(result.error);
                setProgress(100); setFiles(result.files);
                setTimeout(() => setScreen('results'), 800);
            } else {
                const blob = await res.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = "Media_Toolkit_Video.mp4";
                document.body.appendChild(a);
                a.click();
                a.remove();
                setProgress(100);
                setFiles({ vercel: true });
                setTimeout(() => setScreen('results'), 800);
            }
        } catch (err) { clearInterval(timer); setError(err.message); setScreen('preview'); }
    };

    const reset = () => {
        setScreen('input'); setURL(''); setVideoInfo(null);
        setProgress(0); setLogs([]); setFiles([]); setError(null);
        setOptions({ segmenter: false, dubber: false });
    };

    if (screen === 'input') {
        return (
            <div className="container animate-fade">
                <Header title="Paste Media URL" />
                <div className="card">
                    <input
                        className="url-input"
                        placeholder="https://www.youtube.com/watch?v=..."
                        value={url}
                        onChange={e => setURL(e.target.value)}
                        onKeyPress={e => e.key === 'Enter' && fetchVideo()}
                    />
                    {error && <div style={{ color: '#ef4444', marginBottom: 20, textAlign: 'left' }}>⚠️ Error: {error}</div>}
                    <button
                        className="btn-primary"
                        onClick={fetchVideo} disabled={isLoading}
                    >
                        {isLoading ? "🔍 Analyzing Engine..." : "⚡ Start Processing"}
                    </button>
                    <p style={{ marginTop: 20, fontSize: '0.85rem' }}>Bypassing DNS throttles & AI filtering automatically.</p>
                </div>
            </div>
        );
    }

    if (screen === 'preview' && videoInfo) {
        return (
            <div className="container-wide animate-fade">
                <div className="card">
                    <div className="preview-layout">
                        <div className="left-panel">
                            <div className="thumb-container">
                                <img src={videoInfo.thumbnail} className="thumb-large" />
                                <div className="duration-badge">{Math.floor(videoInfo.duration / 60)}:{String(videoInfo.duration % 60).padStart(2, '0')}</div>
                            </div>
                            <div style={{ marginTop: 25 }}>
                                <h3 style={{ color: 'var(--accent)', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: 10 }}>Source Metadata</h3>
                                <h2 style={{ fontSize: '1.4rem', lineHeight: '1.3' }}>{videoInfo.title}</h2>
                                <p>Channel: {videoInfo.uploader}</p>
                            </div>
                        </div>

                        <div className="right-panel">
                            <h3 className="section-title">Step 1: Output Quality</h3>
                            <div className="quality-grid">
                                {videoInfo.formats.map((f, i) => (
                                    <div
                                        key={i}
                                        className={`quality-card ${selectedFormat === f.format_id ? 'active' : ''}`}
                                        onClick={() => setSelectedFormat(f.format_id)}
                                    >
                                        <span className="q-res">{f.quality}</span>
                                        <span className="q-size">{f.mb} MB</span>
                                    </div>
                                ))}
                            </div>

                            <h3 className="section-title">Step 2: AI Enhancements</h3>
                            <div className="options-row">
                                <label className="option-box">
                                    <input type="checkbox" checked={options.segmenter} onChange={e => setOptions({ ...options, segmenter: e.target.checked })} />
                                    <div>
                                        <div style={{ fontWeight: 700 }}>Smart Segment</div>
                                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>30s Clip Extraction</div>
                                    </div>
                                </label>
                                <label className="option-box">
                                    <input type="checkbox" checked={options.dubber} onChange={e => setOptions({ ...options, dubber: e.target.checked })} />
                                    <div>
                                        <div style={{ fontWeight: 700 }}>Neural Dub</div>
                                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>AI Voice Intro</div>
                                    </div>
                                </label>
                            </div>

                            <div className="action-buttons">
                                <button className="btn-secondary" style={{ flex: 1 }} onClick={() => setScreen('input')}>Back</button>
                                <button className="btn-primary" style={{ flex: 2 }} onClick={startDownload}>🚀 Execute Pipeline</button>
                            </div>
                        </div>
                    </div>
                    {error && <div style={{ color: '#ef4444', marginTop: 20 }}>⚠️ Network Error: {error}</div>}
                </div>
            </div>
        );
    }

    if (screen === 'processing') {
        return (
            <div className="container animate-fade">
                <Header title="Engine Executing..." />
                <div className="card">
                    <div className="progress-container">
                        <div className="progress-bar" style={{ width: `${progress}%` }}></div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--accent)', marginBottom: 20, fontSize: '0.9rem', fontWeight: 800 }}>
                        <span>ORCHESTRATING PIPELINE</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="log-window">
                        {logs.map((l, i) => <div key={i} className="log-entry">{l}</div>)}
                        <div id="log-end"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (screen === 'results') {
        const isVercel = files.vercel || (files.length > 0 && files[0].url);

        return (
            <div className="container animate-fade">
                <Header title="Task Finalized" />
                <div className="card" style={{ textAlign: 'center' }}>
                    <div className="success-icon">✨</div>

                    {isVercel ? (
                        <>
                            <h2 style={{ color: '#10b981' }}>File Ready</h2>
                            <p>Processing complete. Your file has been generated.</p>
                        </>
                    ) : (
                        <>
                            <h2 style={{ color: '#10b981' }}>Saved to Desktop!</h2>
                            <div className="file-list">
                                {files.map((f, i) => <div className="file-item" key={i}>📄 {f.filename}</div>)}
                            </div>
                        </>
                    )}

                    <button className="btn-primary" style={{ marginTop: 20 }} onClick={reset}>⚡ Start New Task</button>
                </div>
            </div>
        );
    }

    return null;
}

function Header({ title }) {
    return <div style={{ marginBottom: 40, textAlign: 'center' }}>
        <h1>Media Toolkit</h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{title}</p>
    </div>;
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
