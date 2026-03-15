'use client';

import { useState } from 'react';

export default function TailPage() {

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState("");

  const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api').replace(/\/api$/, '');

  const uploadPdf = async () => {

    if (!file) {
      alert("Please upload a PDF file");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {

      const res = await fetch(
        `${API_BASE}/api/tail/upload`,
        {
          method: "POST",
          body: formData
        }
      );

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      const data = await res.json();

      setDownloadUrl(
        `${API_BASE}/api/tail/download/${data.job_id}`
      );

    } catch (err) {

      console.error(err);
      alert("Conversion failed");

    } finally {

      setLoading(false);

    }

  };

  const resetTool = () => {
    setFile(null);
    setDownloadUrl("");
  };

  return (

    <div style={styles.page}>

      <h2 style={styles.title}>
        Tail Reference Converter
      </h2>

      <p style={styles.subtitle}>
        Upload a PDF file to convert reference tail into XML
      </p>

      <div style={styles.uploadBox}>

        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />

        <br /><br />

        <button
          style={styles.btn}
          onClick={uploadPdf}
          disabled={loading}
        >
          {loading ? "Processing..." : "Convert to XML"}
        </button>

      </div>

      {downloadUrl && (

        <div style={styles.downloadBox}>

          <p>✅ XML Generated Successfully</p>

          <a
            href={downloadUrl}
            style={styles.downloadBtn}
            onClick={resetTool}
          >
            Download XML
          </a>

          <p style={styles.note}>
            File will auto delete after 30 minutes
          </p>

        </div>

      )}

    </div>

  );

}

/* ================= STYLES ================= */

const styles: any = {

  page: {
    maxWidth: "900px",
    margin: "40px auto",
    padding: "40px",
    background: "#ffffff",
    borderRadius: "16px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.08)"
  },

  title: {
    textAlign: "center",
    fontSize: "28px",
    marginBottom: "10px"
  },

  subtitle: {
    textAlign: "center",
    color: "#475569",
    marginBottom: "30px"
  },

  uploadBox: {
    border: "2px dashed #38bdf8",
    padding: "40px",
    borderRadius: "14px",
    textAlign: "center",
    background: "#f8fafc"
  },

  btn: {
    padding: "10px 20px",
    borderRadius: "10px",
    border: "none",
    background: "#38bdf8",
    color: "#fff",
    cursor: "pointer",
    fontWeight: "bold"
  },

  downloadBox: {
    marginTop: "30px",
    textAlign: "center"
  },

  downloadBtn: {
    display: "inline-block",
    marginTop: "10px",
    padding: "10px 18px",
    background: "#22c55e",
    color: "#fff",
    borderRadius: "8px",
    textDecoration: "none"
  },

  note: {
    marginTop: "10px",
    fontSize: "12px",
    color: "#64748b"
  }

};