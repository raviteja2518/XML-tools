'use client';

import { useState, useRef } from 'react';
import axios from 'axios';

type Step = 1 | 2 | 3 | 4 | 5;

export default function CasePdfToXmlPage() {
  const [step, setStep] = useState<Step>(1);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState('');
  const [xmlContent, setXmlContent] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /* ================= RESET ================= */
  const resetTool = () => {
    setStep(1);
    setFile(null);
    setLoading(false);
    setJobId('');
    setXmlContent('');
  };

  /* ================= UPLOAD ================= */
 const uploadFile = async () => {
  if (!file) return alert('Please upload PDF or Word file');

  const fd = new FormData();
  fd.append('file', file);

  setLoading(true);
  setStep(2);

  try {
    const res = await axios.post(
      'http://localhost:8000/api/case-reference/upload',
      fd
    );

    setJobId(res.data.job_id);
    setXmlContent(res.data.preview_xml);
    setLoading(false);
    setStep(3);
  } catch (err: any) {
    setLoading(false);
    setStep(1);

    const msg =
      err?.response?.data?.detail ||
      'Processing failed (check backend logs)';
    alert(msg);
  }
};


  /* ================= UPDATE XML ================= */
  const updateXml = async () => {
    try {
      await axios.post(
        'http://localhost:8000/api/case-reference/update',
        {
          job_id: jobId,
          xml: xmlContent,
        }
      );
      setStep(4);
    } catch {
      alert('Update failed');
    }
  };

  /* ================= DOWNLOAD ================= */
  const downloadXml = async () => {
    try {
      const res = await axios.get(
        `http://localhost:8000/api/case-reference/download?job_id=${jobId}`,
        { responseType: 'blob' }
      );

      const blob = new Blob([res.data], { type: 'application/xml' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'case.xml';
      a.click();
      window.URL.revokeObjectURL(url);

      // 🔥 Reset FE after download
      setTimeout(resetTool, 300);
    } catch {
      alert('Download failed');
    }
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>Case PDF / Word → XML</h2>
      <p style={styles.subtitle}>
        Auto tagging + manual correction + clean XML download
      </p>

      {/* ================= STEP 1 ================= */}
      {step === 1 && (
        <div style={styles.card}>
          <h3>Upload Case PDF / Word</h3>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={e => setFile(e.target.files?.[0] || null)}
          />
          <br /><br />
          <button style={styles.primaryBtn} onClick={uploadFile}>
            Upload & Process
          </button>
        </div>
      )}

      {/* ================= STEP 2 ================= */}
      {step === 2 && (
        <div style={styles.card}>
          <h3>Processing</h3>
          <p style={styles.loadingText}>
            {loading ? '⏳ Auto tagging in progress…' : 'Completed'}
          </p>
        </div>
      )}

      {/* ================= STEP 3 ================= */}
      {step === 3 && (
        <div style={styles.editorCard}>
          <h3>Review & Correct XML</h3>
          <textarea
            ref={textareaRef}
            value={xmlContent}
            onChange={e => setXmlContent(e.target.value)}
            style={styles.textarea}
          />
          <button style={styles.primaryBtn} onClick={updateXml}>
            Confirm & Continue
          </button>
        </div>
      )}

      {/* ================= STEP 4 ================= */}
      {step === 4 && (
        <div style={styles.card}>
          <h3>Final XML Ready</h3>
          <button style={styles.primaryBtn} onClick={downloadXml}>
            Download XML
          </button>
          <p style={styles.success}>
            ✔ File will auto delete after download
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
    height: '65vh',
    background: '#020617',
    color: '#4ade80',
    border: 'none',
    padding: '16px',
    fontSize: '14px',
    borderRadius: '10px',
    outline: 'none',
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
    color: '#2563eb',
    fontSize: '16px',
  },
  success: {
    marginTop: '12px',
    color: '#16a34a',
  },
};
