'use client';

import { useState } from 'react';
import axios from 'axios';

type Step = 1 | 2 | 3 | 4 | 5;

export default function XmlRefPage() {
  const [step, setStep] = useState<Step>(1);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [xmlPath, setXmlPath] = useState('');
  const [analysisProgress, setAnalysisProgress] = useState(0);

  const progress =
    step === 2 ? analysisProgress : (step / 5) * 100;

  /* ================= RESET ================= */
  const resetTool = () => {
    setStep(1);
    setFile(null);
    setLoading(false);
    setXmlPath('');
    setAnalysisProgress(0);
  };

  /* ================= NAV ================= */
  const next = () => step < 5 && setStep((step + 1) as Step);
  const prev = () => step > 1 && setStep((step - 1) as Step);

  /* ================= UPLOAD ================= */
  const handleUpload = async () => {
  if (!file) return alert('Please select a Word file');

  setStep(2);
  setLoading(true);
  setAnalysisProgress(20);

  const fakeProgress = setInterval(() => {
    setAnalysisProgress((p) => (p < 99 ? p + Math.random() * 3 : p));
  }, 400);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await axios.post(
      'http://localhost:8000/api/xml-ref/upload',
      formData
    );

    clearInterval(fakeProgress);
    setAnalysisProgress(100);

    setXmlPath(res.data.xml_file);
    setLoading(false);
    setStep(3);
  } catch (err) {
    clearInterval(fakeProgress);
    alert('Upload failed');
    resetTool();
  }
};


  /* ================= DOWNLOAD ================= */
  const downloadXml = async () => {
    try {
      const res = await axios.get(
        `http://localhost:8000/api/xml-ref/download`,
        {
          params: { path: xmlPath },
          responseType: 'blob',
        }
      );

      const blob = new Blob([res.data], { type: 'application/xml' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = 'references.xml';
      document.body.appendChild(a);
      a.click();

      URL.revokeObjectURL(url);
      a.remove();

      setTimeout(resetTool, 300);
    } catch {
      alert('Download failed');
    }
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>XML Reference Builder</h2>
      <p style={styles.subtitle}>
        Upload a Word document and convert references into structured XML
      </p>

      {/* Progress Bar */}
      <div style={styles.progressWrap}>
        <div style={{ ...styles.progressBar, width: `${progress}%` }} />
      </div>

      <div style={styles.card}>
        {/* STEP 1 */}
        {step === 1 && (
          <>
            <h3 style={styles.stepTitle}>Step 1: Upload Word Document</h3>
            <div style={styles.uploadBox}>
              <input
                type="file"
                accept=".docx"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <br /><br />
              <button style={styles.primaryBtn} onClick={handleUpload}>
                Upload & Analyze
              </button>
            </div>
          </>
        )}

        {/* STEP 2 */}
       {step === 2 && (
  <>
    <h3 style={styles.stepTitle}>Step 2: Analyzing References</h3>
    <p style={styles.centerText}>
      🔍 Processing references… Please wait
    </p>
    <p style={styles.progressText}>
      Progress: {Math.floor(analysisProgress)}%
    </p>
    <p style={{ fontSize: 12, color: '#64748b', textAlign: 'center' }}>
      This may take a few seconds depending on document size
    </p>
  </>
)}


        {/* STEP 3 */}
        {step === 3 && (
          <>
            <h3 style={styles.stepTitle}>Step 3: Tag Mapping</h3>
            <p>✔ References auto-tagged using smart rules</p>
            <button style={styles.primaryBtn} onClick={next}>
              Preview XML
            </button>
          </>
        )}

        {/* STEP 4 */}
        {step === 4 && (
          <>
            <h3 style={styles.stepTitle}>Step 4: XML Preview</h3>
            <pre style={styles.code}>
{`XML generated successfully
Path: ${xmlPath}`}
            </pre>
          </>
        )}

        {/* STEP 5 */}
        {step === 5 && (
          <>
            <h3 style={styles.stepTitle}>Step 5: Download XML</h3>
            <button style={styles.primaryBtn} onClick={downloadXml}>
              Download XML
            </button>
            <p style={styles.successText}>
              ✔ Tool will reset automatically after download
            </p>
          </>
        )}

        {/* NAV */}
        <div style={styles.nav}>
          <button onClick={prev} disabled={step === 1} style={styles.navBtn}>
            Back
          </button>
          <button onClick={next} disabled={step === 5} style={styles.navBtnPrimary}>
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const styles: any = {
  page: {
    maxWidth: '1200px',
    margin: '30px auto',
    padding: '40px',
    background: '#ffffff',
    borderRadius: '16px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
  },
  title: {
    textAlign: 'center',
    fontSize: '30px',
    marginBottom: '8px',
    color: '#020617',
    fontWeight: 600,
  },
  subtitle: {
    textAlign: 'center',
    color: '#475569',
    marginBottom: '30px',
    fontSize: '15px',
  },
  progressWrap: {
    height: '8px',
    background: '#e5e7eb',
    borderRadius: '10px',
    overflow: 'hidden',
    marginBottom: '30px',
  },
  progressBar: {
    height: '100%',
    background: '#38bdf8',
    transition: 'width 0.4s ease',
  },
  card: {
    background: '#f8fafc',
    padding: '30px',
    borderRadius: '16px',
    border: '1px solid #e2e8f0',
  },
  stepTitle: {
    marginBottom: '20px',
    fontSize: '18px',
    color: '#0f172a',
    fontWeight: 600,
  },
  uploadBox: {
    border: '2px dashed #cbd5f5',
    padding: '40px',
    borderRadius: '14px',
    textAlign: 'center',
    background: '#f1f5f9',
  },
  centerText: {
    textAlign: 'center',
    fontSize: '16px',
    color: '#2563eb',
  },
  progressText: {
    textAlign: 'center',
    fontSize: '14px',
    color: '#475569',
  },
  code: {
    background: '#020617',
    color: '#4ade80',
    padding: '20px',
    borderRadius: '10px',
    fontSize: '13px',
    lineHeight: '1.6',
  },
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '30px',
  },
  navBtn: {
    padding: '10px 20px',
    borderRadius: '10px',
    border: '1px solid #cbd5e1',
    background: '#ffffff',
    cursor: 'pointer',
  },
  navBtnPrimary: {
    padding: '10px 22px',
    borderRadius: '10px',
    background: '#38bdf8',
    color: '#ffffff',
    border: 'none',
    cursor: 'pointer',
  },
  primaryBtn: {
    background: '#22c55e',
    color: '#ffffff',
    padding: '10px 20px',
    borderRadius: '10px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
  },
  successText: {
    marginTop: '12px',
    color: '#16a34a',
  },
};
