'use client';

import { useState } from 'react';

type Step = 1 | 2 | 3;

export default function DocBookUploadTool() {
  const [step, setStep] = useState<Step>(1);
  const [file, setFile] = useState<File | null>(null);
  const [type, setType] = useState('');
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');

  const processFile = () => {
    if (!file || !type) {
      alert('Please upload file and select content type');
      return;
    }

    setStep(2);
    setProgress(10);
    setStatus('Uploading Word file...');

    setTimeout(() => {
      setProgress(40);
      setStatus(`Applying ${type} tags...`);
    }, 1000);

    setTimeout(() => {
      setProgress(70);
      setStatus('Generating DocBook XML...');
    }, 2000);

    setTimeout(() => {
      setProgress(100);
      setStatus('Completed successfully');
      setStep(3);
    }, 3000);
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>DocBook Word → XML</h2>
      <p style={styles.subtitle}>
        Front Matter / Chapter / Back Matter tagging tool
      </p>

      {/* ================= STEP 1 ================= */}
      {step === 1 && (
        <div style={styles.card}>
          <h3>Upload Word File</h3>

          <input
            type="file"
            accept=".doc,.docx"
            onChange={e => setFile(e.target.files?.[0] || null)}
          />

          <br /><br />

          <h4>Select Content Type</h4>

          <div>
            <input
              type="radio"
              name="type"
              value="Front Matter"
              onChange={e => setType(e.target.value)}
            /> Front Matter
          </div>

          <div>
            <input
              type="radio"
              name="type"
              value="Chapter"
              onChange={e => setType(e.target.value)}
            /> Chapter
          </div>

          <div>
            <input
              type="radio"
              name="type"
              value="Back Matter"
              onChange={e => setType(e.target.value)}
            /> Back Matter
          </div>

          <button style={styles.primaryBtn} onClick={processFile}>
            Process File
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
        <div style={styles.card}>
          <h3>DocBook XML Ready</h3>
          <p style={styles.success}>
            ✔ XML generated successfully based on selected type
          </p>

          <button style={styles.primaryBtn}>
            Download XML
          </button>
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
