'use client';

import Link from 'next/link';

const TOOLS = [
  {
    name: 'PDF to XML',
    desc: 'Convert PDF files into LN, JATS, BITS XML formats',
    path: '/Tools/pdf-to-xml',
    icon: '📄',
  },
  {
    name: 'LN XML Manual Tagging',
    desc: 'Page-wise tagging and LN XML generation',
    path: '/Tools/manual-tagging',
    icon: '🏷️',
  },
  {
    name: 'PDF Split',
    desc: 'Split PDF by page range and download ZIP',
    path: '/Tools/split-pdf',
    icon: '✂️',
  },
  {
    name: 'PDF to Word',
    desc: 'Convert PDF documents into editable Word files',
    path: '/Tools/pdf-to-word',
    icon: '📝',
  },
  {
    name: 'Image Crop Tool',
    desc: 'Crop images for OCR & publishing workflows',
    path: '/Tools/image_crop',
    icon: '🖼️',
  },
  {
    name: 'OCR Preview',
    desc: 'Preview OCR output page-by-page',
    path: '/Tools/ocr-preview',
    icon: '🔍',
  },
  {
    name: 'Folder Generator',
    desc: 'Auto-create XML project folder structures',
    path: '/Tools/folder_creation',
    icon: '📁',
  },
  {
    name: 'XML REF',
    desc: 'XML project Ref',
    path: '/Tools/xml-ref',
    icon: '📝',
  },
  {
    name: 'LN Case ',
    desc: 'XML project Ref',
    path: '/Tools/case-pdf-to-xml',
    icon: '📝',
  },
   {
    name: 'DocBook XML',
    desc: 'XML project',
    path: '/Tools/docbook',
    icon: '📝',
  },
  {
    name: 'DocBook XML Index',
    desc: 'XML project',
    path: '/Tools/docbook-index',
    icon: '📝',
  },
  {
    name: 'DocBook Bibliography',
    desc: 'XML project',
    path: '/Tools/bibliography',
    icon: '📝',
  },
  {
    name: 'Package Builder',
    desc: 'Create ZIP packages for client delivery',
    path: '/package-builder',
    icon: '📦',
  },
  {
    name: 'XML Validator',
    desc: 'Validate XML against DTD / schema',
    path: '/xml-validator',
    icon: '✅',
  },
];

export default function ToolsPage() {
  return (
    <div style={styles.page}>
      <h2 style={styles.title}>Tools Dashboard</h2>
      <p style={styles.subtitle}>
        Select a tool to start processing your documents
      </p>

      <div style={styles.grid}>
        {TOOLS.map((tool) => (
          <Link key={tool.path} href={tool.path} style={styles.card}>
            <div style={styles.icon}>{tool.icon}</div>
            <h3 style={styles.cardTitle}>{tool.name}</h3>
            <p style={styles.cardDesc}>{tool.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const styles: any = {
  page: {
    maxWidth: '1400px',
    margin: '30px auto',
    padding: '40px',
    background: '#ffffff',
    borderRadius: '16px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
  },

  title: {
    fontSize: '30px',
    textAlign: 'center',
    marginBottom: '8px',
    color: '#020617',
  },

  subtitle: {
    textAlign: 'center',
    color: '#475569',
    marginBottom: '35px',
    fontSize: '15px',
  },

  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
    gap: '22px',
  },

  card: {
    display: 'block',
    padding: '26px',
    borderRadius: '16px',
    background: '#f8fafc',
    border: '1px solid #e2e8f0',
    textDecoration: 'none',
    color: '#020617',
    transition: 'all 0.25s ease',
  },

  icon: {
    fontSize: '36px',
    marginBottom: '12px',
  },

  cardTitle: {
    fontSize: '18px',
    marginBottom: '8px',
    color: '#0f172a',
  },

  cardDesc: {
    fontSize: '14px',
    color: '#475569',
    lineHeight: '1.6',
  },
};
<style jsx>{`
  a:hover {
    transform: translateY(-6px);
    border-color: #38bdf8;
    box-shadow: 0 14px 35px rgba(56, 189, 248, 0.35);
    background: #ecfeff;
  }
`}</style>
