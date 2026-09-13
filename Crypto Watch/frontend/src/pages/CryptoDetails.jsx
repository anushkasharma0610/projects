import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../api';
import { InvestmentCalculator } from './Calculator';
const money=n=>n==null?'—':new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:n<1?6:2}).format(n);
const pct=n=>n==null?'—':`${n>=0?'+':''}${Number(n).toFixed(2)}%`;
export default function CryptoDetails(){
 const {coin_id}=useParams(), [coin,setCoin]=useState(null), [history,setHistory]=useState([]), [prediction,setPrediction]=useState(null), [days,setDays]=useState(30), [error,setError]=useState('');
 useEffect(()=>{api('/api/crypto/'+coin_id).then(setCoin).catch(e=>setError(e.message));api('/api/crypto/'+coin_id+'/prediction').then(setPrediction).catch(e=>setError(e.message))},[coin_id]);
 useEffect(()=>{
   setHistory([]);
   api(`/api/crypto/${coin_id}/history?days=${days}`)
     .then(data => setHistory((data.prices || []).map(point => ({ date: new Date(point[0]).toLocaleDateString(), price: point[1] }))))
     .catch(err => setError(err.message));
 },[coin_id,days]);
 if(error&&!coin)return <div className="page"><div className="error">{error}</div><Link to="/dashboard">Back to dashboard</Link></div>;
 if(!coin)return <div className="page"><p className="empty">Loading cryptocurrency data…</p></div>;
 return <div className="page"><Link className="back" to="/dashboard">← Dashboard</Link><section className="detail-head"><div className="coin-name">{coin.image&&<img src={coin.image}/>}<div><h1>{coin.name}</h1><span>{coin.symbol?.toUpperCase()}</span></div></div><strong>{money(coin.current_price)}</strong></section>{error&&<div className="error">{error}</div>}
 <section className="summary-grid"><Stat label="24h Change" value={pct(coin.price_change_percentage_24h)} up={coin.price_change_percentage_24h>=0}/><Stat label="24h High" value={money(coin.high_24h)}/><Stat label="24h Low" value={money(coin.low_24h)}/><Stat label="Market Cap" value={money(coin.market_cap)}/><Stat label="Volume" value={money(coin.total_volume)}/></section>
 <section className="panel"><div className="panel-head"><div><h2>Historical price</h2><p>USD closing prices from available market data.</p></div><div className="range-buttons">{[[1,'1D'],[7,'7D'],[30,'30D'],[90,'90D'],[365,'1Y']].map(([v,l])=><button key={v} className={days===v?'active':''} onClick={()=>setDays(v)}>{l}</button>)}</div></div>{history.length?<div className="chart-box"><ResponsiveContainer width="100%" height={320}><LineChart data={history}><XAxis dataKey="date" minTickGap={40}/><YAxis domain={['auto','auto']} tickFormatter={x=>'$'+Number(x).toLocaleString()}/><Tooltip formatter={v=>money(v)}/><Line type="monotone" dataKey="price" stroke="#5eead4" strokeWidth={2} dot={false}/></LineChart></ResponsiveContainer></div>:<p className="empty">Loading historical prices…</p>}</section>
 <section className="prediction panel"><h2>Next-Day Estimate</h2>{prediction?<div className="prediction-grid"><Metric label="Current" value={money(prediction.current_price)}/><Metric label="Estimated next-day price" value={money(prediction.predicted_price)}/><Metric label="Expected movement" value={pct(prediction.predicted_change_percent)}/><Metric label="Direction" value={prediction.direction}/><Metric label="Confidence" value={prediction.confidence}/></div>:<p className="empty">Calculating historical-data-based estimate…</p>}<p className="disclaimer">Crypto prices are highly volatile. Predictions shown here are statistical estimates based on historical market data and are not guaranteed. This application does not provide financial advice.</p></section>
 <InvestmentCalculator title={`What if I invested in ${coin.name}?`}/></div>;
}
function Stat({label,value,up}){return <article className="metric"><span>{label}</span><b className={up===undefined?'':up?'positive':'negative'}>{value}</b></article>};function Metric({label,value}){return <article className="metric"><span>{label}</span><b>{value}</b></article>}
