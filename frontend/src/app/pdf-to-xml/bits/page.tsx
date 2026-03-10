"use client";
import { useState, useRef } from "react";

type Step = 1 | 2 | 3 | 4 | 5;

type FrontMatter = {
  title: string;
  subtitle: string;
  edition: string;
  publisher: string;
};

export default function BitsXmlBuilder() {
  const [step, setStep] = useState<Step>(1);
  const [frontMatter, setFrontMatter] = useState<FrontMatter | null>(null);

  const progress = (step / 5) * 100;

  const next = () =>
    setStep(s => (s < 5 ? ((s + 1) as Step) : s));
  const back = () =>
    setStep(s => (s > 1 ? ((s - 1) as Step) : s));

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>BITS XML Builder</h1>
      <p style={styles.subtitle}>
        Meta XML → Front Matter → Chapters → References → Final XML
      </p>

      {/* Progress */}
      <div style={styles.progressWrap}>
        <div style={{ ...styles.progressBar, width: `${progress}%` }} />
      </div>

      {/* Stepper */}
      <div style={styles.stepper}>
        {["Meta XML", "Front", "Chapters", "References", "Final"].map(
          (s, i) => (
            <div
              key={i}
              style={{
                ...styles.step,
                background: step === i + 1 ? "#10b2f1" : "#e5e7eb",
                color: step === i + 1 ? "#fff" : "#000",
              }}
            >
              {i + 1}. {s}
            </div>
          )
        )}
      </div>

      {/* Content */}
      <div style={styles.card}>
        {step === 1 && <MetaUpload onNext={next} />}
        {step === 2 && (
          <FrontMatterForm
            onSubmit={data => {
              setFrontMatter(data);
              next();
            }}
          />
        )}
        {step === 3 && <Placeholder title="Chapters + Manual Tagging" />}
        {step === 4 && <Placeholder title="References Conversion" />}
        {step === 5 && <Placeholder title="Final BITS XML Download" />}
      </div>

      {/* Nav */}
      <div style={styles.nav}>
        <button disabled={step === 1} onClick={back}>
          ← Back
        </button>
        {step !== 2 && (
          <button onClick={next}>
            {step === 5 ? "Finish" : "Next →"}
          </button>
        )}
      </div>
    </div>
  );
}

/* ================= STEP 1 ================= */

function MetaUpload({ onNext }: { onNext: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  return (
    <>
      <h3>Upload Meta XML</h3>

      <input
        ref={inputRef}
        type="file"
        accept=".xml"
        hidden
        onChange={e => setFile(e.target.files?.[0] || null)}
      />

      <div
        style={styles.uploadBox}
        onClick={() => inputRef.current?.click()}
      >
        {file ? file.name : "Click to upload Meta XML"}
      </div>

      <button
        style={styles.primaryBtn}
        onClick={() => {
          if (!file) return alert("Upload Meta XML first");
          onNext();
        }}
      >
        Extract Metadata
      </button>
    </>
  );
}

/* ================= STEP 2 ================= */

function FrontMatterForm({
  onSubmit,
}: {
  onSubmit: (data: FrontMatter) => void;
}) {
  const [form, setForm] = useState<FrontMatter>({
    title: "",
    subtitle: "",
    edition: "",
    publisher: "",
  });

  return (
    <>
      <h3>Book Front Matter</h3>

      <input
        style={styles.input}
        placeholder="Book Title"
        value={form.title}
        onChange={e => setForm({ ...form, title: e.target.value })}
      />
      <input
        style={styles.input}
        placeholder="Subtitle"
        value={form.subtitle}
        onChange={e => setForm({ ...form, subtitle: e.target.value })}
      />
      <input
        style={styles.input}
        placeholder="Edition"
        value={form.edition}
        onChange={e => setForm({ ...form, edition: e.target.value })}
      />
      <input
        style={styles.input}
        placeholder="Publisher"
        value={form.publisher}
        onChange={e => setForm({ ...form, publisher: e.target.value })}
      />

      <button
        style={styles.primaryBtn}
        onClick={() => {
          if (!form.title || !form.publisher) {
            alert("Title and Publisher required");
            return;
          }
          onSubmit(form);
        }}
      >
        Save & Continue
      </button>
    </>
  );
}

/* ================= PLACEHOLDER ================= */

function Placeholder({ title }: { title: string }) {
  return <h3>{title} (Next phase)</h3>;
}

/* ================= STYLES ================= */

const styles: any = {
  page: {
    maxWidth: 1100,
    margin: "40px auto",
    padding: 40,
    background: "#fff",
    borderRadius: 16,
    boxShadow: "0 10px 40px rgba(0,0,0,0.08)",
  },
  title: { fontSize: 32 },
  subtitle: { color: "#475569", marginBottom: 20 },

  progressWrap: {
    height: 8,
    background: "#e5e7eb",
    borderRadius: 20,
    overflow: "hidden",
    marginBottom: 20,
  },
  progressBar: {
    height: "100%",
    background: "#10b2f1",
  },

  stepper: {
    display: "flex",
    gap: 10,
    marginBottom: 30,
  },
  step: {
    flex: 1,
    padding: 10,
    textAlign: "center",
    borderRadius: 8,
    fontWeight: "bold",
  },

  card: {
    padding: 30,
    border: "1px solid #e5e7eb",
    borderRadius: 14,
    background: "#f8fafc",
  },

  uploadBox: {
    border: "2px dashed #10b2f1",
    borderRadius: 14,
    padding: 40,
    textAlign: "center",
    cursor: "pointer",
    marginBottom: 20,
    fontWeight: "bold",
  },

  input: {
    width: "100%",
    padding: 12,
    marginBottom: 12,
    borderRadius: 8,
    border: "1px solid #cbd5e1",
  },

  primaryBtn: {
    padding: "12px 20px",
    background: "#10b2f1",
    border: "none",
    borderRadius: 8,
    fontWeight: "bold",
    cursor: "pointer",
  },

  nav: {
    marginTop: 30,
    display: "flex",
    justifyContent: "space-between",
  },
};
