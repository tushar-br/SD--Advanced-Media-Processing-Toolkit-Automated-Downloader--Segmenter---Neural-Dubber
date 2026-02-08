
const { useState, useEffect } = React;
const API_Base = "http://localhost:5000/api";

function App() {
    // STATE
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

    // ACTIONS
    const fetchVideo = async () => {
        if (!url) return alert("Please enter a YouTube URL first!");
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
            // AUTO SELECT FIRST OPTION (Because we sorted it by Quality)
            if (data.formats && data.formats.length > 0) {
                setSelectedFormat(data.formats[0].format_id);
            }
            setScreen('preview');
        } catch (err) { setError(err.message); }
        finally { setIsLoading(false); }
    };

    const startDownload = async () => {
        setScreen('processing'); setProgress(10); setLogs(["🚀 Initializing Job..."]);
        const timer = setInterval(() => {
            setProgress(p => (p >= 90 ? p : p + 5));
            setLogs(l => [...l.slice(-4), "⏳ Processing..."]);
        }, 800);
        try {
            const res = await fetch(`${API_Base}/process`, {
                method: 'POST', body: JSON.stringify({
                    url, format: selectedFormat,
                    enable_segmenter: options.segmenter, enable_dubber: options.dubber
                }), headers: { 'Content-Type': 'application/json' }
            });
            clearInterval(timer);
            const result = await res.json();
            if (!result.success) throw new Error(result.error);
            setProgress(100); setFiles(result.files);
            setTimeout(() => setScreen('results'), 1000);
        } catch (err) { clearInterval(timer); setError(err.message); setScreen('preview'); }
    };

    const reset = () => {
        setScreen('input'); setURL(''); setVideoInfo(null);
        setProgress(0); setLogs([]); setFiles([]); setError(null);
        setOptions({ segmenter: false, dubber: false });
    };

    // RENDER: INPUT (Small Card)
    if (screen === 'input') {
        return (
            <div className="container animate-fade">
                <Header title="Paste Media URL" />
                <div className="card">
                    <input
                        className="url-input"
                        placeholder="Paste YouTube Link here..."
                        value={url}
                        onChange={e => setURL(e.target.value)}
                        onKeyPress={e => e.key === 'Enter' && fetchVideo()}
                    />
                    {error && <div style={{ color: '#ef4444', marginBottom: 20 }}>⚠️ {error}</div>}
                    <button
                        className="btn-primary"
                        onClick={fetchVideo} disabled={isLoading}
                    >
                        {isLoading ? "Fetching Info..." : "🔍 Search Video"}
                    </button>
                </div>
            </div>
        );
    }

    // RENDER: PREVIEW (Wide Dashboard)
    if (screen === 'preview' && videoInfo) {
        return (
            <div className="container-wide animate-fade">
                <div className="card">
                    <div className="preview-layout">

                        {/* LEFT: VISUAL */}
                        <div className="left-panel">
                            <div className="thumb-container">
                                <img src={videoInfo.thumbnail} className="thumb-large" />
                                <div className="duration-badge">{Math.floor(videoInfo.duration / 60)}:{String(videoInfo.duration % 60).padStart(2, '0')}</div>
                            </div>
                            <div style={{ marginTop: 20 }}>
                                <h2>{videoInfo.title}</h2>
                                <p>By {videoInfo.uploader} • {Number(videoInfo.views).toLocaleString()} views</p>
                            </div>
                        </div>

                        {/* RIGHT: CONFIGURATION */}
                        <div className="right-panel">
                            <h3 className="section-title">Select Quality</h3>
                            <div className="quality-grid">
                                {videoInfo.formats.map((f, i) => (
                                    <div
                                        key={i}
                                        className={`quality-card ${selectedFormat === f.format_id ? 'active' : ''}`}
                                        onClick={() => setSelectedFormat(f.format_id)}
                                    >
                                        <span className="q-res">{f.quality}</span>
                                        <span className="q-size">{f.filesize_mb} MB</span>
                                    </div>
                                ))}
                            </div>

                            <h3 className="section-title">AI Enhancements</h3>
                            <div className="options-row">
                                <label className="option-box">
                                    <input type="checkbox" checked={options.segmenter} onChange={e => setOptions({ ...options, segmenter: e.target.checked })} />
                                    <div>
                                        <strong>Auto Segmenter</strong>
                                        <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Split 30s clips</div>
                                    </div>
                                </label>
                                <label className="option-box">
                                    <input type="checkbox" checked={options.dubber} onChange={e => setOptions({ ...options, dubber: e.target.checked })} />
                                    <div>
                                        <strong>Neural Dub</strong>
                                        <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>AI Voice Demo</div>
                                    </div>
                                </label>
                            </div>

                            <div className="action-buttons">
                                <button className="btn-secondary" style={{ flex: 1 }} onClick={() => setScreen('input')}>Cancel</button>
                                <button className="btn-primary" style={{ flex: 2 }} onClick={startDownload}>📥 Download Now</button>
                            </div>

                            {error && <div style={{ color: '#ef4444', marginTop: 20 }}>⚠️ {error}</div>}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // RENDER: PROCESSING
    if (screen === 'processing') {
        return (
            <div className="container animate-fade">
                <Header title="Processing Media..." />
                <div className="card">
                    <div style={{ height: 10, background: '#334155', borderRadius: 5, marginBottom: 15, overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${progress}%`, background: '#8b5cf6', transition: 'width 0.3s' }}></div>
                    </div>
                    <div style={{ textAlign: 'right', color: '#94a3b8', marginBottom: 20 }}>{progress}% Completed</div>
                    <div style={{ background: '#0f172a', padding: 15, borderRadius: 8, height: 150, overflowY: 'auto', color: '#94a3b8', fontSize: '0.9rem', fontFamily: 'monospace' }}>
                        {logs.map((l, i) => <div key={i}>{l}</div>)}
                    </div>
                </div>
            </div>
        );
    }

    // RENDER: RESULTS
    if (screen === 'results') {
        const isVercel = files.vercel || (files.length > 0 && files[0].url);

        return (
            <div className="container animate-fade">
                <Header title="Success!" />
                <div className="card" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '4rem', marginBottom: 20 }}>✅</div>

                    {isVercel ? (
                        <>
                            <h2 style={{ color: '#10b981' }}>File Ready for Download!</h2>
                            <p>Click below to save to your device.</p>
                            <a
                                href={files.download_url}
                                target="_blank"
                                className="btn-primary"
                                style={{ display: 'block', marginTop: 20, textDecoration: 'none', lineHeight: '50px' }}
                            >
                                ⬇️ Click to Save File
                            </a>
                        </>
                    ) : (
                        <>
                            <h2 style={{ color: '#10b981' }}>Files Saved to Desktop!</h2>
                            <div className="file-list">
                                {files.map((f, i) => <div className="file-item" key={i}>📄 {f.filename}</div>)}
                            </div>
                        </>
                    )}

                    <button className="btn-secondary" style={{ marginTop: 20, width: '100%' }} onClick={reset}>Process Another Video</button>
                </div>
            </div>
        );
    }

    return null;
}

function Header({ title }) {
    return <div style={{ marginBottom: 30 }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: 10 }}>Media Toolkit</h1>
        <p style={{ fontSize: '1.1rem' }}>{title}</p>
    </div>;
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
