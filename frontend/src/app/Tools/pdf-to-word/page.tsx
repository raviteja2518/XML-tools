'use client';

import { useState, useRef } from 'react';
import axios from 'axios';

const API = 'http://127.0.0.1:8000';

export default function PdfToWordOCR() {
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
      const res = await axios.post(
        `${API}/tools/pdf-to-word-ocr`,
        fd
      );

      listenProgress(res.data.job_id);
      setDownloadUrl(`${API}${res.data.download_url}`);
    } catch {
      alert('OCR failed');
      setLoading(false);
    }
  };

  /* ================= SSE PROGRESS ================= */
  const listenProgress = (jobId: string) => {
    const es = new EventSource(
      `${API}/events/pdf-to-word-ocr-progress/${jobId}`
    );

    eventSourceRef.current = es;

    es.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setProgress(data.progress);

      if (data.progress >= 100) {
        es.close();
        setLoading(false);
      }
    };

    es.onerror = () => {
      es.close();
      setLoading(false);
    };
  };

  /* ================= RESET AFTER DOWNLOAD ================= */
  const reset = () => {
    setFile(null);
    setProgress(0);
    setDownloadUrl('');
    setLoading(false);

    if (fileRef.current) fileRef.current.value = '';
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>PDF → Word (OCR)</h2>
      <p style={styles.subtitle}>
        Convert scanned PDF files into editable Word documents
      </p>

      {/* Upload Box */}
      <label style={styles.uploadBox}>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          hidden
          onChange={(e) =>
            setFile(e.target.files?.[0] || null)
          }
        />

        {!file ? (
          <>
            <div style={styles.uploadIcon}>📄</div>
            <p style={styles.uploadText}>Click to upload PDF</p>
            <span style={styles.uploadHint}>
              Scanned PDFs supported
            </span>
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
          opacity: loading ? 0.6 : 1,
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
                width: `${progress}%`,
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

/* ================= STYLES (MATCH PREVIOUS TOOLS) ================= */

const styles: any = {
  page: {
    maxWidth: '760px',
    margin: '50px auto',
    padding: '42px',
    background: '#ffffff',
    borderRadius: '18px',
    boxShadow: '0 15px 40px rgba(2, 6, 23, 0.12)',
    textAlign: 'center',
  },

  title: {
    fontSize: '28px',
    fontWeight: '700',
    marginBottom: '10px',
    color: '#020617',
  },

  subtitle: {
    fontSize: '15px',
    color: '#475569',
    marginBottom: '32px',
  },

  uploadBox: {
    border: '2px dashed #38bdf8',
    borderRadius: '16px',
    padding: '36px',
    cursor: 'pointer',
    marginBottom: '26px',
    background: '#f0f9ff',
    display: 'block',
  },

  uploadIcon: {
    fontSize: '46px',
    marginBottom: '10px',
  },

  uploadText: {
    fontWeight: '600',
    fontSize: '15px',
    color: '#0369a1',
  },

  uploadHint: {
    fontSize: '13px',
    color: '#64748b',
  },

  fileSize: {
    display: 'block',
    fontSize: '13px',
    color: '#64748b',
    marginTop: '6px',
  },

  convertBtn: {
    width: '100%',
    padding: '15px',
    fontSize: '16px',
    borderRadius: '12px',
    border: 'none',
    background: '#38bdf8',
    color: '#020617',
    fontWeight: '700',
    cursor: 'pointer',
  },

  progressWrap: {
    marginTop: '22px',
  },

  progressOuter: {
    width: '100%',
    height: '10px',
    background: '#e5e7eb',
    borderRadius: '10px',
    overflow: 'hidden',
  },

  progressInner: {
    height: '10px',
    background: '#38bdf8',
    transition: 'width 0.4s ease',
  },

  progressText: {
    marginTop: '8px',
    fontSize: '14px',
    color: '#334155',
  },

  downloadBox: {
    marginTop: '28px',
  },

  downloadBtn: {
    display: 'inline-block',
    padding: '12px 26px',
    background: '#0ea5e9',
    color: '#ffffff',
    borderRadius: '12px',
    textDecoration: 'none',
    fontWeight: '700',
    fontSize: '15px',
  },
};
