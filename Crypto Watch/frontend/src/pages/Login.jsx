import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { api } from '../api';
export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' }), [error, setError] = useState(''), [loading, setLoading] = useState(false); const nav = useNavigate();
  async function submit(e) { e.preventDefault(); setError(''); setLoading(true); try { const data = await api('/api/auth/login', {method:'POST', body:JSON.stringify(form)}); localStorage.setItem('cryptowatch_token', data.access_token); localStorage.setItem('cryptowatch_user', JSON.stringify(data.user)); nav('/dashboard'); } catch(err) { setError(err.message); } finally { setLoading(false); } }
  return <div className="auth-page"><form className="auth-card" onSubmit={submit}><div className="brand auth-brand">Crypto<span>Watch</span></div><h1>Welcome back</h1><p>Sign in to follow the markets you care about.</p>{error && <div className="error">{error}</div>}<label>Email<input type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label><label>Password<input type="password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label><button disabled={loading}>{loading?'Signing in…':'Sign In'}</button><p className="center">Don't have an account? <Link to="/signup">Sign Up</Link></p></form></div>;
}
