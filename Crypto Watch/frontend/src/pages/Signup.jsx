import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { api } from '../api';
export default function Signup() {
  const [form, setForm] = useState({name:'',email:'',password:'',confirm:''}), [error,setError]=useState(''), [loading,setLoading]=useState(false); const nav=useNavigate();
  async function submit(e) { e.preventDefault(); if(form.password!==form.confirm) return setError('Passwords do not match.'); setError(''); setLoading(true); try { await api('/api/auth/signup',{method:'POST',body:JSON.stringify({name:form.name,email:form.email,password:form.password})}); nav('/login', {state:{message:'Account created. Please sign in.'}}); } catch(err){setError(err.message)} finally{setLoading(false)} }
  return <div className="auth-page"><form className="auth-card" onSubmit={submit}><div className="brand auth-brand">Crypto<span>Watch</span></div><h1>Create account</h1><p>Start a simple, personal crypto watchlist.</p>{error&&<div className="error">{error}</div>}<label>Name<input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label><label>Email<input type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label><label>Password<input type="password" minLength="8" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label><label>Confirm Password<input type="password" required value={form.confirm} onChange={e=>setForm({...form,confirm:e.target.value})}/></label><button disabled={loading}>{loading?'Creating…':'Create Account'}</button><p className="center">Already have an account? <Link to="/login">Sign In</Link></p></form></div>;
}
