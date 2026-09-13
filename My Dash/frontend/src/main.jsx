import React, { useCallback, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Responsive, WidthProvider } from 'react-grid-layout/legacy';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import './styles.css';

const Grid = WidthProvider(Responsive);
const api = async (path, options = {}) => {
  const response = await fetch(`/api${path}`, { credentials: 'include', headers: { 'Content-Type': 'application/json', ...options.headers }, ...options });
  if (response.status === 204) return null;
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Something went wrong');
  return data;
};

function Auth({ onSignedIn }) {
  const [mode, setMode] = useState('signin'); const [username, setUsername] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState('');
  async function submit(event) { event.preventDefault(); setError(''); try { onSignedIn(await api(`/auth/${mode}`, { method: 'POST', body: JSON.stringify({ username, password }) })); } catch (err) { setError(err.message); } }
  return <main className="auth-shell"><section className="auth-card"><p className="eyebrow">YOUR SPACE, YOUR WAY</p><h1>My Dash</h1><p className="muted">A dashboard arranged around how you work.</p><form onSubmit={submit}><label>Username<input value={username} onChange={event => setUsername(event.target.value)} required minLength="3" autoComplete="username" /></label><label>Password<input type="password" value={password} onChange={event => setPassword(event.target.value)} required minLength="8" autoComplete={mode === 'signin' ? 'current-password' : 'new-password'} /></label>{error && <p className="error">{error}</p>}<button>{mode === 'signin' ? 'Sign in' : 'Create account'}</button></form><button className="text-button" onClick={() => setMode(mode === 'signin' ? 'signup' : 'signin')}>{mode === 'signin' ? 'New here? Create an account' : 'Already have an account? Sign in'}</button></section></main>;
}

function Clock({ config = {}, updateConfig }) {
  const [now, setNow] = useState(new Date());
  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  const timezone = config.timezone || browserTimezone;
  const hour12 = config.hour12 ?? false;
  const look = config.look || 'classic';
  const timezones = [...new Set([browserTimezone, 'UTC', 'Asia/Kolkata', 'Asia/Tokyo', 'Asia/Dubai', 'Europe/London', 'Europe/Paris', 'America/New_York', 'America/Chicago', 'America/Los_Angeles', 'Australia/Sydney'])];
  useEffect(() => { const id = setInterval(() => setNow(new Date()), 1000); return () => clearInterval(id); }, []);
  const formatter = new Intl.DateTimeFormat([], { timeZone: timezone, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12 });
  const date = new Intl.DateTimeFormat([], { timeZone: timezone, weekday: 'long', month: 'long', day: 'numeric' }).format(now);
  return <div className={`clock clock-${look}`}><div className="widget-controls"><select aria-label="Clock timezone" value={timezone} onChange={event => updateConfig({ timezone: event.target.value })}>{timezones.map(zone => <option key={zone} value={zone}>{zone}</option>)}</select><button type="button" className="small-button" onClick={() => updateConfig({ hour12: !hour12 })}>{hour12 ? '12-hour' : '24-hour'}</button></div><div className="widget-controls"><select aria-label="Clock appearance" value={look} onChange={event => updateConfig({ look: event.target.value })}><option value="classic">Classic</option><option value="neon">Neon</option><option value="minimal">Minimal</option></select></div><b>{formatter.format(now)}</b><span>{date}</span><small>{timezone}</small></div>;
}

function Crypto({ config = {}, updateConfig }) {
  const ids = config.ids || ['bitcoin', 'ethereum', 'solana', 'binancecoin']; const [coins, setCoins] = useState([]); const [query, setQuery] = useState(''); const [results, setResults] = useState([]);
  const reload = useCallback(() => api(`/crypto?ids=${encodeURIComponent(ids.join(','))}`).then(setCoins).catch(() => setCoins([])), [ids.join(',')]);
  useEffect(() => { reload(); }, [reload]);
  useEffect(() => { if (!query.trim()) return setResults([]); const timer = setTimeout(() => api(`/crypto/search?q=${encodeURIComponent(query)}`).then(setResults).catch(() => setResults([])), 300); return () => clearTimeout(timer); }, [query]);
  function addCoin(coin) { if (!ids.includes(coin.id)) updateConfig({ ids: [...ids, coin.id] }); setQuery(''); setResults([]); }
  function removeCoin(id) { updateConfig({ ids: ids.filter(item => item !== id) }); }
  return <div className="crypto-widget"><div className="search-wrap"><input aria-label="Search cryptocurrencies" placeholder="Search any crypto" value={query} onChange={event => setQuery(event.target.value)} />{results.length > 0 && <div className="search-results">{results.map(coin => <button key={coin.id} type="button" onClick={() => addCoin(coin)}><b>{coin.symbol.toUpperCase()}</b> {coin.name}</button>)}</div>}</div><div className="coin-list">{coins.length ? coins.map(coin => <div className="coin" key={coin.id}><span><b>{coin.symbol.toUpperCase()}</b><small>{coin.name}</small></span><span><button className="remove-button" title="Remove from watchlist" onClick={() => removeCoin(coin.id)}>×</button><b>${coin.current_price?.toLocaleString()}</b><small className={coin.price_change_percentage_24h >= 0 ? 'positive' : 'negative'}>{coin.price_change_percentage_24h?.toFixed(2)}% today</small></span></div>) : <p className="muted">Add cryptocurrencies to your watchlist.</p>}</div></div>;
}

function Music() {
  const [query, setQuery] = useState(''); const [video, setVideo] = useState(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(false);
  async function play(event) { event.preventDefault(); if (!query.trim()) return; setLoading(true); setError(''); try { setVideo(await api(`/music/search?q=${encodeURIComponent(query)}`)); } catch (err) { setError(err.message); } finally { setLoading(false); } }
  return <div className="music"><form onSubmit={play}><input aria-label="Search music" placeholder="Song, artist, or album" value={query} onChange={event => setQuery(event.target.value)} /><button disabled={loading}>{loading ? 'Finding…' : 'Play'}</button></form>{error && <p className="error">{error}</p>}{video ? <iframe key={video.video_id} title={`Now playing: ${video.query}`} src={`https://www.youtube-nocookie.com/embed/${video.video_id}?autoplay=1&controls=1&rel=0`} allow="autoplay; encrypted-media; picture-in-picture" allowFullScreen /> : <p className="muted music-empty">Search to play music here.</p>}</div>;
}

function Notes() { const [notes, setNotes] = useState([]); const [text, setText] = useState(''); const reload = () => api('/notes').then(setNotes); useEffect(reload, []); async function add(event) { event.preventDefault(); if (!text.trim()) return; await api('/notes', { method: 'POST', body: JSON.stringify({ content: text }) }); setText(''); reload(); } return <div className="notes"><form onSubmit={add}><textarea value={text} onChange={event => setText(event.target.value)} placeholder="Write a note…" /><button>Add</button></form>{notes.map(note => <article key={note.id}>{note.content}<button aria-label="Delete note" onClick={async () => { await api(`/notes/${note.id}`, { method: 'DELETE' }); reload(); }}>×</button></article>)}</div>; }

function Github() {
  const [repos, setRepos] = useState([]); const [repository, setRepository] = useState(''); const [error, setError] = useState(''); const [checking, setChecking] = useState(false); const [changed, setChanged] = useState([]);
  const reload = () => api('/repositories').then(setRepos).catch(() => {}); useEffect(reload, []);
  async function add(event) { event.preventDefault(); setError(''); try { await api('/repositories', { method: 'POST', body: JSON.stringify({ repository }) }); setRepository(''); reload(); } catch (err) { setError(err.message); } }
  async function check() { setChecking(true); setError(''); try { const result = await api('/repositories/check', { method: 'POST' }); setChanged(result.changed_ids); reload(); } catch (err) { setError(err.message); } finally { setChecking(false); } }
  useEffect(() => { check(); }, []);
  return <div className="github"><form onSubmit={add}><input placeholder="owner/repository" value={repository} onChange={event => setRepository(event.target.value)} /><button>Add repo</button></form><button className="small-button" onClick={check} disabled={checking}>{checking ? 'Checking…' : 'Check all repositories'}</button>{error && <p className="error">{error}</p>}<div className="repo-list">{repos.length ? repos.map(repo => <article key={repo.id} className={changed.includes(repo.id) ? 'repo-changed' : ''}><div><a href={`https://github.com/${repo.owner}/${repo.name}`} target="_blank" rel="noreferrer">{repo.owner}/{repo.name}</a><small>{repo.last_message || 'No commit information'}</small></div><button className="remove-button" title="Stop monitoring" onClick={async () => { await api(`/repositories/${repo.id}`, { method: 'DELETE' }); reload(); }}>×</button>{changed.includes(repo.id) && <strong>Updated</strong>}</article>) : <p className="muted">Add public repositories to monitor their latest commit.</p>}</div></div>;
}

const widgetComponents = { clock: Clock, crypto: Crypto, music: Music, notes: Notes, github: Github };
function Dashboard({ user, onSignout }) {
  const [items, setItems] = useState([]); const [theme, setTheme] = useState(user.theme);
  useEffect(() => { api('/dashboard').then(({ widgets }) => setItems(widgets)); }, []); useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  const persist = useCallback(next => { setItems(next); api('/dashboard', { method: 'PUT', body: JSON.stringify({ widgets: next }) }).catch(() => {}); }, []);
  const saveLayout = useCallback(layout => persist(items.map(widget => { const change = layout.find(entry => entry.i === widget.id); return change ? { ...widget, x: change.x, y: change.y, w: change.w, h: change.h } : widget; })), [items, persist]);
  const updateWidget = useCallback((id, changes) => persist(items.map(widget => widget.id === id ? { ...widget, config: { ...(widget.config || {}), ...changes } } : widget)), [items, persist]);
  async function switchTheme() { const next = theme === 'dark' ? 'light' : 'dark'; setTheme(next); await api('/me/settings', { method: 'PATCH', body: JSON.stringify({ theme: next }) }); }
  return <main className="dashboard"><header><div><p className="eyebrow">PERSONAL DASHBOARD</p><h1>Good to see you, {user.username}.</h1></div><div className="header-actions"><button className="icon-button" title="Toggle theme" onClick={switchTheme}>{theme === 'dark' ? '☀' : '◐'}</button><button className="text-button" onClick={onSignout}>Sign out</button></div></header><p className="help">Drag by a widget header and resize from its lower-right corner. Your layout and settings save automatically.</p><Grid className="layout" layouts={{ lg: items.map(widget => ({ i: widget.id, x: widget.x, y: widget.y, w: widget.w, h: widget.h })) }} breakpoints={{ lg: 1000, md: 700, sm: 0 }} cols={{ lg: 12, md: 8, sm: 1 }} rowHeight={72} resizeHandles={['se']} onLayoutChange={saveLayout} draggableHandle=".widget-title">{items.map(widget => { const Component = widgetComponents[widget.type]; return <section key={widget.id} className="widget"><div className="widget-title"><span>{widget.title}</span><span className="drag">⠿</span></div><div className="widget-body"><Component config={widget.config} updateConfig={changes => updateWidget(widget.id, changes)} /></div></section>; })}</Grid></main>;
}

function App() { const [user, setUser] = useState(null); const [loading, setLoading] = useState(true); useEffect(() => { api('/me').then(setUser).catch(() => {}).finally(() => setLoading(false)); }, []); if (loading) return <main className="loading">Loading…</main>; return user ? <Dashboard user={user} onSignout={async () => { try { await api('/auth/signout', { method: 'POST' }); } finally { setUser(null); } }} /> : <Auth onSignedIn={setUser} />; }
createRoot(document.getElementById('root')).render(<App />);
