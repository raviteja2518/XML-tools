'use client';

import { useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';

type Step = 1 | 2 | 3 | 4;

export default function OCRDocBookPreview() {
  const [step, setStep] = useState<Step>(1);
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [xmlPreview, setXmlPreview] = useState('');
  const [jobId, setJobId] = useState('');

  /* ================= START PROCESS ================= */
  const startProcessing = async () => {
    if (!file) {
      alert('Please upload converted Word file');
      return;
    }

    const fd = new FormData();
    fd.append('file', file);

    setStep(2);
    setProgress(10);
    setStatus('Uploading file...');

    try {
      const token = Cookies.get('token');
      const res = await axios.post(
        'http://localhost:8000/api/ocr-docbook/upload',
        fd,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      setJobId(res.data.job_id);
      setTotalPages(res.data.total_pages || 1);

      setProgress(40);
      setStatus('Applying OCR rules...');

      setTimeout(() => {
        setProgress(70);
        setStatus('Preparing page previews...');
      }, 1000);

      setTimeout(() => {
        setProgress(100);
        setStatus('Processing completed');
        loadPagePreview(1, res.data.job_id);
        setStep(3);
      }, 2000);

    } catch (err: any) {
      alert(err?.response?.data?.detail || 'OCR processing failed');
      setStep(1);
    }
  };

  /* ================= PAGE PREVIEW ================= */
  const loadPagePreview = async (page: number, jid = jobId) => {
    try {
      setCurrentPage(page);

      const token = Cookies.get('token');
      const res = await axios.get(
        'http://localhost:8000/api/ocr-docbook/page-preview',
        { 
          params: { job_id: jid, page },
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      setXmlPreview(res.data.xml);
    } catch {
      alert('Failed to load page preview');
    }
  };

  /* ================= DOWNLOAD WORD FILE ================= */
  const downloadWord = async () => {
    try {
      const token = Cookies.get('token');
      const res = await axios.get(
        'http://localhost:8000/api/ocr-docbook/download',
        {
          params: { job_id: jobId },
          responseType: 'blob',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      // ✅ Correct MIME type for Word
      const blob = new Blob(
        [res.data],
        {
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
      );

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'ocr_docbook.docx';
      a.click();
      window.URL.revokeObjectURL(url);

      // 🔥 Reset UI after download
      setStep(1);
      setFile(null);
      setJobId('');
      setXmlPreview('');
      setProgress(0);
      setStatus('');
      setCurrentPage(1);
      setTotalPages(0);

    } catch {
      alert('Download failed');
    }
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>🔍 OCR for DocBook</h2>
      <p style={styles.subtitle}>
        Page-by-page OCR preview with DocBook tagging rules
      </p>

      {/* ================= STEP 1 ================= */}
      {step === 1 && (
        <div style={styles.card}>
          <h3>Upload PDF → Word Converted File</h3>

          <input
            type="file"
            accept=".doc,.docx"
            onChange={e => setFile(e.target.files?.[0] || null)}
          />

          <button style={styles.primaryBtn} onClick={startProcessing}>
            Upload & Process
          </button>
        </div>
      )}

      {/* ================= STEP 2 ================= */}
      {step === 2 && (
        <div style={styles.card}>
          <h3>Processing OCR Rules</h3>

          <div style={styles.progressBar}>
            <div
              style={{
                ...styles.progressFill,
                width: `${progress}%`,
              }}
            />
          </div>

          <p style={styles.loadingText}>
            {progress}% — {status}
          </p>
        </div>
      )}

      {/* ================= STEP 3 ================= */}
      {step === 3 && (
        <div style={styles.editorCard}>
          <h3 style={{ color: '#e5e7eb' }}>
            Page {currentPage} / {totalPages}
          </h3>

          <div style={styles.pageNav}>
            <button
              disabled={currentPage === 1}
              onClick={() => loadPagePreview(currentPage - 1)}
            >
              ◀ Prev
            </button>

            <button
              disabled={currentPage === totalPages}
              onClick={() => loadPagePreview(currentPage + 1)}
            >
              Next ▶
            </button>
          </div>

          <textarea
            value={xmlPreview}
            readOnly
            style={styles.textarea}
          />

          <button
            style={styles.primaryBtn}
            onClick={() => setStep(4)}
          >
            Finalize & Download
          </button>
        </div>
      )}

      {/* ================= STEP 4 ================= */}
      {step === 4 && (
        <div style={styles.card}>
          <h3>Word File Ready</h3>
          <button style={styles.primaryBtn} onClick={downloadWord}>
            Download Word (.docx)
          </button>
          <p style={styles.success}>
            ✔ Files auto-deleted after download / 30 mins expiry
          </p>
        </div>
      )}
    </div>
  );
}

/* ================= STYLES ================= */

const styles: any = {
  page: {
    maxWidth: '1200px',
    margin: '30px auto',
    padding: '40px',
    background: '#fff',
    borderRadius: '16px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
  },
  title: {
    textAlign: 'center',
    fontSize: '30px',
    fontWeight: 600,
  },
  subtitle: {
    textAlign: 'center',
    color: '#475569',
    marginBottom: '30px',
  },
  card: {
    background: '#f8fafc',
    padding: '30px',
    borderRadius: '14px',
    border: '1px solid #e2e8f0',
    textAlign: 'center',
  },
  editorCard: {
    background: '#020617',
    padding: '20px',
    borderRadius: '14px',
  },
  textarea: {
    width: '100%',
    height: '55vh',
    background: '#020617',
    color: '#4ade80',
    border: 'none',
    padding: '16px',
    fontSize: '14px',
    borderRadius: '10px',
    outline: 'none',
    fontFamily: 'Consolas, monospace',
  },
  primaryBtn: {
    marginTop: '20px',
    padding: '10px 22px',
    background: '#38bdf8',
    border: 'none',
    borderRadius: '10px',
    fontWeight: 'bold',
    cursor: 'pointer',
  },
  loadingText: {
    marginTop: '12px',
    color: '#2563eb',
    fontSize: '16px',
  },
  success: {
    marginTop: '12px',
    color: '#16a34a',
    fontSize: '16px',
    fontWeight: 500,
  },
  progressBar: {
    height: '12px',
    background: '#e5e7eb',
    borderRadius: '10px',
    overflow: 'hidden',
    marginTop: '20px',
  },
  progressFill: {
    height: '100%',
    background: '#22c55e',
    transition: 'width 0.4s ease',
  },
  pageNav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px',
    color: '#e5e7eb',
  },
};
