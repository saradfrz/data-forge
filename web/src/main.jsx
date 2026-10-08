import React, {useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';
function Plot({rows,field,title,unit}) {
 const points=rows.map((r,i)=>[Date.parse(r.window_start||r.sample_end),Number(r[field]),r]).filter(([i,y,r])=>r[field]!==null&&Number.isFinite(y)&&Number.isFinite(i));
 if(!points.length)return <section><h2>{title}</h2><p>No eligible observations.</p></section>;
 const xmin=Math.min(...points.map(p=>p[0])), xmax=Math.max(...points.map(p=>p[0]));
 const ys=points.map(p=>p[1]), min=Math.min(...ys),max=Math.max(...ys),range=max-min||1;
 return <section><h2>{title}</h2><p>{unit} · UTC event time · {points.length} values</p><svg role="img" aria-label={title} viewBox="0 0 900 180">
 {points.map(([i,y,r])=><circle key={i} cx={30+(i-xmin)/Math.max(xmax-xmin,1)*840} cy={150-(y-min)/range*120} r="2.5"><title>{r.window_start||r.sample_end}: {y}</title></circle>)}
 <text x="5" y="16">{max.toPrecision(6)}</text><text x="5" y="175">{min.toPrecision(6)}</text></svg>
 <small>{rows[0]?.window_start||rows[0]?.sample_end} → {rows.at(-1)?.window_start||rows.at(-1)?.sample_end}</small></section>;
}
function Candles({rows}) {
 if(!rows.length)return <section><h2>OHLC</h2><p>No observations.</p></section>;
 const lo=Math.min(...rows.map(r=>+r.low)),hi=Math.max(...rows.map(r=>+r.high)),span=hi-lo||1;
 const x=t=>35+(Date.parse(t)-Date.parse(rows[0].window_start))/Math.max(1,Date.parse(rows.at(-1).window_start)-Date.parse(rows[0].window_start))*830;
 const y=p=>160-(+p-lo)/span*130;
 return <section><h2>Quote OHLC</h2><p>Quote currency per base unit · UTC event time · gaps are empty</p><svg viewBox="0 0 900 190" role="img" aria-label="OHLC candles">{rows.map((r,i)=><g key={i} className={+r.close>=+r.open?'up':'down'}><title>{JSON.stringify(r)}</title><line x1={x(r.window_start)} x2={x(r.window_start)} y1={y(r.high)} y2={y(r.low)}/><rect x={x(r.window_start)-2} y={Math.min(y(r.open),y(r.close))} width="4" height={Math.max(1,Math.abs(y(r.open)-y(r.close)))}/></g>)}<text x="5" y="15">{hi.toFixed(5)}</text><text x="5" y="185">{lo.toFixed(5)}</text></svg><small>{rows[0].window_start} → {rows.at(-1).window_start}</small></section>;
}
function App(){
 const [data,setData]=useState(null),[error,setError]=useState(''),[mode,setMode]=useState('static');
 const [pair,setPair]=useState('EURUSD'),[basis,setBasis]=useState('mid'),[interval,setCandleInterval]=useState(60);
 const [start,setStart]=useState(''),[end,setEnd]=useState('');
 useEffect(()=>{let active=true;const load=()=>fetch(mode==='static'?'./snapshot.json':'/api/snapshot').then(r=>{if(!r.ok)throw Error('No published snapshot or backend offline');return r.json()}).then(d=>{if(active){setData(d);setError('');}}).catch(e=>{if(active)setError(e.message);});load();const timer=mode==='live'?setInterval(load,60000):null;return()=>{active=false;clearInterval(timer);};},[mode]);
 if(!data)return <main><h1>Data Forge</h1><p>{error||'Loading snapshot…'}</p></main>;
 const filter=rows=>(rows||[]).filter(r=>r.instrument===pair&&(!start||String(r.window_start||r.sample_end||r.event_date)>=start)&&(!end||String(r.window_start||r.sample_end||r.event_date)<end));
 const table=data.tables||{}, cs=filter(table.gold_candles).filter(r=>r.price_basis===basis&&r.interval_seconds===+interval).slice(0,2000);
 const pairs=[...new Set((table.gold_candles||[]).map(r=>r.instrument))];
 return <main><header><div><p className="eyebrow">FINANCIAL DATA ENGINEERING LAB</p><h1>Data Forge</h1></div><span className="badge">{data.synthetic?'SYNTHETIC':'HISTORICAL'} · {data.run==='reference-only'?'STATIC REFERENCE':'SNAPSHOT'}</span></header>
 <p>Deterministic FX replay · Bronze → Silver → Gold</p>
 <nav><label>Data mode <select value={mode} onChange={e=>setMode(e.target.value)}><option value="static">Bundled synthetic demo</option><option value="live">Local cluster snapshot</option></select></label><label>Pair <select value={pair} onChange={e=>setPair(e.target.value)}>{pairs.map(p=><option key={p}>{p}</option>)}</select></label><label>Price basis <select value={basis} onChange={e=>setBasis(e.target.value)}>{['mid','bid','ask'].map(x=><option key={x}>{x}</option>)}</select></label><label>Interval <select value={interval} onChange={e=>setCandleInterval(+e.target.value)}>{[1,60,3600].map(x=><option key={x} value={x}>{x}s</option>)}</select></label><label>UTC from <input placeholder="2026-09-15" value={start} onChange={e=>setStart(e.target.value)}/></label><label>UTC before <input placeholder="2026-09-16" value={end} onChange={e=>setEnd(e.target.value)}/></label></nav>
 {error&&<p role="alert">{error}. Showing last successful snapshot.</p>}
 {Object.values(data.truncated||{}).some(Boolean)&&<p role="alert">Bounded preview: some tables were truncated. Full tables remain in MinIO.</p>}
 <Candles rows={cs}/><div className="grid"><Plot rows={filter(table.gold_spreads)} field="mean_spread_pips" title="Observation-weighted spread" unit="Pips"/><Plot rows={filter(table.gold_returns).map(r=>({...r,simple_return:r.simple_return===null?null:r.simple_return*100}))} field="simple_return" title="One-minute simple returns" unit="Percent"/><Plot rows={filter(table.gold_volatility).map(r=>({...r,rolling_log_vol_60m:r.rolling_log_vol_60m===null?null:r.rolling_log_vol_60m*100}))} field="rolling_log_vol_60m" title="Rolling volatility · 60 returns" unit="Percent per one-minute return"/><Plot rows={cs} field="tick_count" title="Quote activity" unit="Source observations; not trade volume"/></div>
 <section><h2>Daily summary · UTC</h2><div className="scroll"><table><thead><tr>{['Pair','Day','Ticks','Spread pips','Open–close %','Realized vol %','Coverage','Complete'].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{filter(table.gold_daily_summary).map((r,i)=><tr key={i}><td>{r.instrument}</td><td>{r.event_date}</td><td>{r.tick_count}</td><td>{Number(r.mean_spread_pips).toFixed(3)}</td><td>{(r.open_close_return*100).toFixed(4)}</td><td>{r.realized_vol_daily===null?'—':(r.realized_vol_daily*100).toFixed(4)}</td><td>{(r.return_coverage*100).toFixed(1)}%</td><td>{r.complete_day?'Yes':'Partial / unverified'}</td></tr>)}</tbody></table></div></section>
 <div className="grid"><section><h2>Publication health</h2><p>Generated: {data.generated_at}</p><p>Dataset: {data.dataset}</p><p>Run: {data.run}</p><p>This is a captured snapshot, not live-market freshness or a live broker-lag monitor.</p></section><section><h2>Reconciliation</h2><strong>{data.reconciliation?.status||'not compared'}</strong><pre>{JSON.stringify(data.reconciliation,null,2)}</pre></section></div><footer>Educational quote analytics. No trade execution. Prices, coverage and revisions matter.</footer></main>;
}
createRoot(document.getElementById('root')).render(<App/>);
