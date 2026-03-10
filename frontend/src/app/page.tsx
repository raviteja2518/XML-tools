'use client';

export default function HomePage() {
  return (
    <div style={styles.container}>

      {/* ================= HERO ================= */}
      <section style={styles.hero}>
        <h1 style={styles.heroTitle}>
          One Platform for All PDF Conversion Needs
        </h1>

        <p style={styles.heroSub}>
          XML Tools helps publishers, accessibility vendors, and enterprises
          convert PDFs into XML, EPUB, Word, and Images using industry-standard
          workflows.
        </p>

        <div style={styles.heroButtons}>
          <button style={styles.primaryBtn}>Upload PDF</button>
          <button style={styles.secondaryBtn}>Explore Tools</button>
        </div>
      </section>

      {/* ================= PLATFORM INTRO ================= */}
      <section style={styles.introSection}>
        <h2 style={styles.sectionTitle}>Why XML Tools?</h2>
        <p style={styles.introText}>
          Modern publishing requires more than simple PDF conversion.
          XML Tools provides structured, scalable, and standards-compliant
          conversion pipelines suitable for journals, books, and accessibility
          workflows.
        </p>
      </section>

      {/* ================= TOOLS ================= */}
      <section style={styles.toolsSection}>
        <h2 style={styles.sectionTitle}>Our Conversion Tools</h2>

        <div style={styles.toolsGrid}>
          {tools.map((tool, index) => (
            <div key={index} style={styles.toolCard}>
              <h3 style={styles.toolTitle}>{tool.title}</h3>
              <p style={styles.toolDesc}>{tool.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ================= USE CASES ================= */}
      <section style={styles.useCaseSection}>
        <h2 style={styles.sectionTitle}>Who Is This For?</h2>

        <div style={styles.useCaseGrid}>
          <div style={styles.useCaseCard}>📘 Publishers & Journals</div>
          <div style={styles.useCaseCard}>♿ Accessibility Vendors</div>
          <div style={styles.useCaseCard}>🏢 Enterprises & Archives</div>
          <div style={styles.useCaseCard}>📚 E-Book Creators</div>
        </div>
      </section>

      {/* ================= FOOTER ================= */}
      <footer style={styles.footer}>
        <p>© {new Date().getFullYear()} XML Tools. All rights reserved.</p>
      </footer>
    </div>
  );
}

/* ================= DATA ================= */

const tools = [
  {
    title: 'PDF to XML',
    desc: 'Convert PDFs into structured JATS, BITS, LN or custom XML formats suitable for publishing workflows.',
  },
  {
    title: 'PDF to Word',
    desc: 'Generate editable DOCX files while preserving layout and content accuracy.',
  },
  {
    title: 'OCR Processing',
    desc: 'Extract text from scanned PDFs using advanced OCR pipelines.',
  },
  {
    title: 'PDF to TIFF',
    desc: 'Convert PDF pages into high-resolution TIFF images for print and archival use.',
  },
  {
    title: 'PDF Splitter',
    desc: 'Split PDFs by pages, ranges, or chapters for modular processing.',
  },
  {
    title: 'EPUB2 Creation',
    desc: 'Create EPUB2 files compatible with legacy e-readers.',
  },
  {
    title: 'EPUB3 Creation',
    desc: 'Generate modern EPUB3 files with semantic structure and accessibility support.',
  },
];

/* ================= STYLES ================= */

const styles: any = {
  container: {
    fontFamily: 'Arial, sans-serif',
    background: '#f9fafb',
    minHeight: '100vh',
  },

  hero: {
    textAlign: 'center',
    padding: '90px 20px',
    background: 'linear-gradient(135deg, #020617, #0f172a)',
    color: '#fff',
  },

  heroTitle: {
    fontSize: '44px',
    maxWidth: '900px',
    margin: '0 auto',
  },

  heroSub: {
    marginTop: '20px',
    fontSize: '18px',
    color: '#cbd5f5',
    maxWidth: '800px',
    marginInline: 'auto',
  },

  heroButtons: {
    marginTop: '35px',
    display: 'flex',
    justifyContent: 'center',
    gap: '16px',
  },

  primaryBtn: {
    background: '#38bdf8',
    color: '#000',
    padding: '14px 26px',
    borderRadius: '8px',
    border: 'none',
    fontWeight: 'bold',
    cursor: 'pointer',
  },

  secondaryBtn: {
    background: 'transparent',
    color: '#fff',
    padding: '14px 26px',
    borderRadius: '8px',
    border: '1px solid #38bdf8',
    cursor: 'pointer',
  },

  introSection: {
    padding: '70px 30px',
    textAlign: 'center',
    background: '#ffffff',
  },

  introText: {
    maxWidth: '850px',
    margin: '0 auto',
    fontSize: '17px',
    color: '#334155',
  },

  toolsSection: {
    padding: '70px 40px',
  },

  sectionTitle: {
    textAlign: 'center',
    fontSize: '30px',
    marginBottom: '45px',
  },

  toolsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
    gap: '24px',
  },

  toolCard: {
    background: '#fff',
    padding: '24px',
    borderRadius: '14px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.08)',
  },

  toolTitle: {
    marginBottom: '10px',
    color: '#020617',
  },

  toolDesc: {
    color: '#475569',
    fontSize: '14px',
    lineHeight: 1.6,
  },

  useCaseSection: {
    padding: '70px 40px',
    background: '#f1f5f9',
  },

  useCaseGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '20px',
    maxWidth: '1000px',
    margin: '0 auto',
  },

  useCaseCard: {
    background: '#fff',
    padding: '22px',
    textAlign: 'center',
    borderRadius: '12px',
    fontWeight: 'bold',
    boxShadow: '0 6px 16px rgba(0,0,0,0.08)',
  },

  footer: {
    textAlign: 'center',
    padding: '22px',
    background: '#020617',
    color: '#94a3b8',
  },
};
