'use client';

import { useState, useRef } from 'react';
import api from '@/utils/api';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/api$/, '') + '/api';

export default function PdfToWord() {

  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const fileRef = useRef<HTMLInputElement | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  /* ================= CONVERT ================= */

  const convert = async () => {

    if (!file) {
      alert('Please upload a PDF file');
      return;
    }

    setLoading(true);
    setProgress(0);
    setDownloadUrl('');

    const fd = new FormData();
    fd.append('file', file);

    try {

      const res = await api.post(
        `/tools/pdf-to-word`,
        fd
      );

      const jobId = res.data.job_id;

      setDownloadUrl(`${API_BASE}${res.data.download_url}`);

      listenProgress(jobId);

    } catch (err: any) {
      const msg = err.response?.data?.detail || "Conversion failed";
      alert(msg);
      setLoading(false);
    }

  };


  /* ================= PROGRESS ================= */

  const listenProgress = (jobId: string) => {

    const es = new EventSource(
      `${API_BASE}/events/pdf-to-word-progress/${jobId}`
    );

    eventSourceRef.current = es;

    es.onmessage = (e) => {

      const data = JSON.parse(e.data);

      // Job failed on server
      if (data.progress === -1 || data.status === 'failed') {
        es.close();
        setLoading(false);
        alert(`Conversion failed: ${data.error || 'Unknown server error'}`);
        return;
      }

      setProgress(data.progress);

      if (data.progress >= 100) {
        es.close();
        setLoading(false);
      }

    };

    es.onerror = () => {
      es.close();
      setLoading(false);
      alert('Connection to server lost. Please try again.');
    };

  };


  /* ================= RESET ================= */

  const reset = () => {

    setFile(null);
    setProgress(0);
    setDownloadUrl('');
    setLoading(false);

    if (fileRef.current) fileRef.current.value = '';

  };


  return (

    <div style={styles.page}>

      <h2 style={styles.title}>
        PDF → Word Converter
      </h2>

      <p style={styles.subtitle}>
        Convert PDF files into editable Word documents while preserving layout.
      </p>


      {/* Upload */}

      <label style={styles.uploadBox}>

        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          hidden
          onChange={(e)=>setFile(e.target.files?.[0] || null)}
        />

        {!file ? (
          <>
            <div style={styles.uploadIcon}>📄</div>
            <p style={styles.uploadText}>Click to upload PDF</p>
            <span style={styles.uploadHint}>Layout preserved</span>
          </>
        ) : (
          <>
            <strong>{file.name}</strong>
            <span style={styles.fileSize}>
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </>
        )}

      </label>


      {/* Convert Button */}

      <button
        onClick={convert}
        disabled={loading}
        style={{
          ...styles.convertBtn,
          opacity: loading ? 0.6 : 1
        }}
      >

        {loading ? 'Processing…' : 'Convert to Word'}

      </button>


      {/* Progress */}

      {loading && (

        <div style={styles.progressWrap}>

          <div style={styles.progressOuter}>

            <div
              style={{
                ...styles.progressInner,
                width: `${progress}%`
              }}
            />

          </div>

          <p style={styles.progressText}>
            {progress}% completed
          </p>

        </div>

      )}


      {/* Download */}

      {progress === 100 && downloadUrl && (

        <div style={styles.downloadBox}>

          <a
            href={downloadUrl}
            style={styles.downloadBtn}
            onClick={reset}
          >

            Download Word

          </a>

        </div>

      )}

    </div>

  );

}


/* ================= STYLES ================= */

const styles:any = {

  page:{
    maxWidth:'760px',
    margin:'50px auto',
    padding:'42px',
    background:'#ffffff',
    borderRadius:'18px',
    boxShadow:'0 15px 40px rgba(2,6,23,0.12)',
    textAlign:'center'
  },

  title:{
    fontSize:'28px',
    fontWeight:'700',
    marginBottom:'10px',
    color:'#020617'
  },

  subtitle:{
    fontSize:'15px',
    color:'#475569',
    marginBottom:'32px'
  },

  uploadBox:{
    border:'2px dashed #38bdf8',
    borderRadius:'16px',
    padding:'36px',
    cursor:'pointer',
    marginBottom:'26px',
    background:'#f0f9ff',
    display:'block'
  },

  uploadIcon:{
    fontSize:'46px',
    marginBottom:'10px'
  },

  uploadText:{
    fontWeight:'600',
    fontSize:'15px',
    color:'#0369a1'
  },

  uploadHint:{
    fontSize:'13px',
    color:'#64748b'
  },

  fileSize:{
    display:'block',
    fontSize:'13px',
    color:'#64748b',
    marginTop:'6px'
  },

  convertBtn:{
    width:'100%',
    padding:'15px',
    fontSize:'16px',
    borderRadius:'12px',
    border:'none',
    background:'#38bdf8',
    color:'#020617',
    fontWeight:'700',
    cursor:'pointer'
  },

  progressWrap:{
    marginTop:'22px'
  },

  progressOuter:{
    width:'100%',
    height:'10px',
    background:'#e5e7eb',
    borderRadius:'10px',
    overflow:'hidden'
  },

  progressInner:{
    height:'10px',
    background:'#38bdf8',
    transition:'width 0.4s ease'
  },

  progressText:{
    marginTop:'8px',
    fontSize:'14px',
    color:'#334155'
  },

  downloadBox:{
    marginTop:'28px'
  },

  downloadBtn:{
    display:'inline-block',
    padding:'12px 26px',
    background:'#0ea5e9',
    color:'#ffffff',
    borderRadius:'12px',
    textDecoration:'none',
    fontWeight:'700',
    fontSize:'15px'
  }

};