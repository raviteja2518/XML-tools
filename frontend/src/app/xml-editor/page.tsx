'use client';
import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';

const TAGS = ['p', 'h2', 'h3'];

export default function XmlEditor() {
  const [jobId, setJobId] = useState('');
  const [page, setPage] = useState(1);
  const [text, setText] = useState('');
  const [selection, setSelection] = useState<{start:number,end:number}|null>(null);

  useEffect(() => {
    const token = Cookies.get('token');
    fetch(`http://127.0.0.1:8000/xml/job/${jobId}/page/${page}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(d => setText(d.text));
  }, [page, jobId]);

  const applyTag = async (tag: string) => {
    if (!selection) return;
    const token = Cookies.get('token');
    await fetch(`http://127.0.0.1:8000/xml/job/${jobId}/annotate`, {
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ page, tag, ...selection })
    });
    setSelection(null);
  };

  return (
    <div style={{padding:30}}>
      <h2>Manual XML Tagging</h2>

      {/* Toolbar */}
      <div>
        {TAGS.map(t =>
          <button key={t} onClick={() => applyTag(t)}>{t.toUpperCase()}</button>
        )}
      </div>

      {/* Viewer */}
      <pre
        style={{border:'1px solid #ccc',padding:20,minHeight:300}}
        onMouseUp={() => {
          const sel = window.getSelection();
          if (!sel || !sel.rangeCount) return;
          const r = sel.getRangeAt(0);
          setSelection({start:r.startOffset,end:r.endOffset});
        }}
      >
        {text}
      </pre>

      {/* Nav */}
      <div>
        <button onClick={()=>setPage(p=>p-1)} disabled={page===1}>Prev</button>
        <span> Page {page} </span>
        <button onClick={()=>setPage(p=>p+1)}>Next</button>
      </div>

      {/* Generate */}
      <button onClick={()=>{
        const token = Cookies.get('token');
        fetch(`http://127.0.0.1:8000/xml/job/${jobId}/generate`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      }}>
        Generate XML
      </button>
    </div>
  );
}
