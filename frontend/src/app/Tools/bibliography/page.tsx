'use client';

import { useState } from 'react';

type Step = 1 | 2 | 3;

export default function BibliographyTool() {
  const [step, setStep] = useState<Step>(1);
  const [file, setFile] = useState<File | null>(null);
  const [text, setText] = useState('');
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [xmlPreview, setXmlPreview] = useState('');

  const processBibliography = () => {
    if (!file && !text.trim()) {
      alert('Please upload file or enter bibliography text');
      return;
    }

    setStep(2);
    setProgress(10);
    setStatus('Reading bibliography data...');

    setTimeout(() => {
      setProgress(40);
      setStatus('Identifying references...');
    }, 1000);

    setTimeout(() => {
      setProgress(70);
      setStatus('Applying bibliography XML tags...');
    }, 2000);

    setTimeout(() => {
      setProgress(100);
      setStatus('Bibliography XML generated');
      setXmlPreview(
`<bibliography>
  <biblioentry>
    <author>John Doe</author>
    <title>XML Publishing Guide</title>
    <year>2023</year>
  </biblioentry>
</bibliography>`
      );
      setStep(3);
    }, 3000);
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>Bibliography → XML Tool</h2>
      <p style={styles.subtitle}>
        Convert references into clean Bibliography XML
      </p>

      {/* ================= STEP 1 ================= */}
      {step === 1 && (
        <div style={styles.card}>
          <h3>Upload or Enter Bibliography</h3>

          <input
            type="file"
            accept=".doc,.docx,.txt"
            onChange={e => setFile(e.target.files?.[0] || null)}
          />

          <p style={{ margin: '12px 0', fontWeight: 500 }}>OR</p>

          <textarea
            placeholder="Paste bibliography references here..."
            value={text}
            onChange={e => setText(e.target.value)}
            style={{
              ...styles.textarea,
              height: '180px',
              background: '#fff',
              color: '#000',
            }}
          />

          <button style={styles.primaryBtn} onClick={processBibliography}>
            Process Bibliography
          </button>
        </div>
      )}

      {/* ================= STEP 2 ================= */}
      {step === 2 && (
        <div style={styles.card}>
          <h3>Processing</h3>

          <div style={{ marginTop: '20px' }}>
            <div
              style={{
                height: '12px',
                background: '#e5e7eb',
                borderRadius: '10px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${progress}%`,
                  background: '#22c55e',
                  transition: 'width 0.4s ease',
                }}
              />
            </div>
          </div>

          <p style={styles.loadingText}>
            {progress}% — {status}
          </p>
        </div>
      )}

      {/* ================= STEP 3 ================= */}
      {step === 3 && (
        <div style={styles.editorCard}>
          <h3 style={{ color: '#e5e7eb' }}>Bibliography XML Preview</h3>

          <textarea
            value={xmlPreview}
            onChange={e => setXmlPreview(e.target.value)}
            style={styles.textarea}
          />

          <button style={styles.primaryBtn}>
            Download Bibliography XML
          </button>

          <p style={styles.success}>
            ✔ Bibliography XML ready
          </p>
        </div>
      )}
    </div>
  );
}

/* ================= STYLES (Same as Other Tools) ================= */

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
    height: '60vh',
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
};
