import React from 'react';
import { Navigate, NavLink, Route, Routes, useNavigate } from 'react-router-dom';
import { clearSession, token } from './api';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import CryptoDetails from './pages/CryptoDetails';
import Calculator from './pages/Calculator';

function Layout({ children }) {
  const navigate = useNavigate();
  // Older sessions or manually edited browser storage must never stop the UI rendering.
  let user = null;
  try { user = JSON.parse(localStorage.getItem('cryptowatch_user') || 'null'); } catch { clearSession(); }
  const logout = () => { clearSession(); navigate('/login'); };
  return <><header className="topbar"><NavLink className="brand" to="/dashboard">Crypto<span>Watch</span></NavLink><nav><NavLink to="/dashboard">Dashboard</NavLink><NavLink to="/calculator">Calculator</NavLink></nav><div className="user-nav"><span>Welcome, {user?.name || 'Investor'}</span><button className="link-btn" onClick={logout}>Logout</button></div></header><main>{children}</main></>;
}
function Private({ children }) { return token() ? <Layout>{children}</Layout> : <Navigate to="/login" replace />; }
class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error) { return { error }; }
  render() { return this.state.error ? <div className="auth-page"><div className="auth-card"><div className="brand">Crypto<span>Watch</span></div><h1>Unable to load the page</h1><p>Please refresh the browser. If this continues, clear this site's local storage and sign in again.</p><div className="error">{this.state.error.message}</div></div></div> : this.props.children; }
}
export default function App() { return <ErrorBoundary><Routes>
  <Route path="/" element={token() ? <Navigate to="/dashboard" replace /> : <Login />} />
  <Route path="/login" element={token() ? <Navigate to="/dashboard" /> : <Login />} />
  <Route path="/signup" element={token() ? <Navigate to="/dashboard" /> : <Signup />} />
  <Route path="/dashboard" element={<Private><Dashboard /></Private>} />
  <Route path="/crypto/:coin_id" element={<Private><CryptoDetails /></Private>} />
  <Route path="/calculator" element={<Private><Calculator /></Private>} />
  <Route path="*" element={<Navigate to={token() ? '/dashboard' : '/'} replace />} />
</Routes></ErrorBoundary>; }
