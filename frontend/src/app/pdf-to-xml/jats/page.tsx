'use client';

import { useState } from 'react';

export default function JatsXmlPage() {
  const [activeSection, setActiveSection] = useState('front');

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>PDF to JATS XML</h2>
      <p style={styles.subtitle}>
        Build Journal Article Tag Suite (JATS) XML
        using structured, section-wise tagging.
      </p>

      {/* ================= MAIN LAYOUT ================= */}
      <div style={styles.layout}>
        {/* LEFT: SECTIONS */}
        <div style={styles.sidebar}>
          <h4 style={styles.sideTitle}>JATS Sections</h4>

          <button
            style={sectionBtn(activeSection === 'front')}
            onClick={() => setActiveSection('front')}
          >
            Front Matter
          </button>

          <button
            style={sectionBtn(activeSection === 'body')}
            onClick={() => setActiveSection('body')}
          >
            Body
          </button>

          <button
            style={sectionBtn(activeSection === 'back')}
            onClick={() => setActiveSection('back')}
          >
            Back Matter
          </button>
        </div>

        {/* RIGHT: WORKSPACE */}
        <div style={styles.workspace}>
          {activeSection === 'front' && (
            <Section
              title="Front Matter"
              desc="Journal metadata, article title, authors, abstract, keywords"
              tags={[
                '<journal-meta>',
                '<article-title>',
                '<contrib-group>',
                '<abstract>',
                '<kwd-group>',
              ]}
            />
          )}

          {activeSection === 'body' && (
            <Section
              title="Body"
              desc="Main article content divided into sections"
              tags={[
                '<sec>',
                '<title>',
                '<p>',
                '<fig>',
                '<table-wrap>',
              ]}
            />
          )}

          {activeSection === 'back' && (
            <Section
              title="Back Matter"
              desc="References, acknowledgements, appendices"
              tags={[
                '<ref-list>',
                '<ref>',
                '<ack>',
                '<app-group>',
              ]}
            />
          )}
        </div>
      </div>

      {/* ================= XML PREVIEW ================= */}
      <div style={styles.preview}>
        <h4>JATS XML Preview</h4>
        <pre style={styles.xmlBox}>
{`<article>
  <front>...</front>
  <body>...</body>
  <back>...</back>
</article>`}
        </pre>
      </div>
    </div>
  );
}

/* ================= REUSABLE SECTION ================= */

function Section({
  title,
  desc,
  tags,
}: {
  title: string;
  desc: string;
  tags: string[];
}) {
  return (
    <div>
      <h3>{title}</h3>
      <p style={{ color: '#475569', marginBottom: '15px' }}>
        {desc}
      </p>

      <div style={styles.tagGrid}>
        {tags.map((tag) => (
          <div key={tag} style={styles.tagCard}>
            {tag}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const styles: any = {
  page: {
    maxWidth: '1100px',
    margin: '40px auto',
    padding: '40px',
    background: '#ffffff',
    borderRadius: '16px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
  },

  title: {
    fontSize: '28px',
    textAlign: 'center',
    marginBottom: '8px',
  },

  subtitle: {
    fontSize: '15px',
    color: '#475569',
    textAlign: 'center',
    marginBottom: '30px',
  },

  layout: {
    display: 'flex',
    gap: '20px',
  },

  sidebar: {
    width: '260px',
    background: '#f8fafc',
    borderRadius: '12px',
    padding: '20px',
    border: '1px solid #e2e8f0',
  },

  sideTitle: {
    marginBottom: '15px',
    fontSize: '16px',
  },

  workspace: {
    flex: 1,
    background: '#f1f5f9',
    borderRadius: '12px',
    padding: '25px',
    border: '1px solid #e2e8f0',
  },

  tagGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
    gap: '12px',
  },

  tagCard: {
    padding: '10px',
    background: '#ecfeff',
    border: '1px solid #38bdf8',
    borderRadius: '8px',
    fontSize: '13px',
    textAlign: 'center',
    cursor: 'pointer',
  },

  preview: {
    marginTop: '30px',
    padding: '20px',
    background: '#020617',
    color: '#e5e7eb',
    borderRadius: '12px',
  },

  xmlBox: {
    fontSize: '13px',
    whiteSpace: 'pre-wrap',
  },
};

/* ================= HELPERS ================= */

const sectionBtn = (active: boolean) => ({
  width: '100%',
  padding: '10px',
  marginBottom: '10px',
  borderRadius: '8px',
  border: 'none',
  cursor: 'pointer',
  fontWeight: 'bold',
  background: active ? '#38bdf8' : '#e2e8f0',
  color: active ? '#020617' : '#020617',
});
