'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function PdfToXmlPage() {
  const [hovered, setHovered] = useState<string | null>(null);

  const cardStyle = (id: string) => ({
    ...styles.card,
    ...(hovered === id ? styles.cardHover : {}),
  });

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>PDF to XML</h2>
      <p style={styles.subtitle}>
        Convert PDF files into industry-standard XML formats.
        Choose the required XML type below.
      </p>

      <div style={styles.grid}>
        <Link
          href="/pdf-to-xml/jats"
          style={cardStyle('jats')}
          onMouseEnter={() => setHovered('jats')}
          onMouseLeave={() => setHovered(null)}
        >
          <h3>JATS XML</h3>
          <p>Journal Article Tag Suite (Academic Publishing)</p>
        </Link>

        <Link
          href="/pdf-to-xml/bits"
          style={cardStyle('bits')}
          onMouseEnter={() => setHovered('bits')}
          onMouseLeave={() => setHovered(null)}
        >
          <h3>BITS XML</h3>
          <p>Books Interchange Tag Suite</p>
        </Link>

        <Link
          href="/pdf-to-xml/bis"
          style={cardStyle('bis')}
          onMouseEnter={() => setHovered('bis')}
          onMouseLeave={() => setHovered(null)}
        >
          <h3>BIS XML</h3>
          <p>Bureau of Indian Standards XML</p>
        </Link>

        <Link
          href="/pdf-to-xml/ln"
          style={cardStyle('ln')}
          onMouseEnter={() => setHovered('ln')}
          onMouseLeave={() => setHovered(null)}
        >
          <h3>LN XML</h3>
          <p>LexisNexis / Legal XML Format</p>
        </Link>

        <Link
          href="/pdf-to-xml/court"
          style={cardStyle('court')}
          onMouseEnter={() => setHovered('court')}
          onMouseLeave={() => setHovered(null)}
        >
          <h3>Courte Cases</h3>
          <p>LexisNexis / Legal XML Format</p>
        </Link>

      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const styles: any = {
  page: {
    maxWidth: '1000px',
    margin: '40px auto',
    padding: '40px',
    background: '#ffffff',
    borderRadius: '16px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
  },

  title: {
    fontSize: '28px',
    marginBottom: '8px',
    textAlign: 'center',
  },

  subtitle: {
    fontSize: '15px',
    color: '#475569',
    marginBottom: '40px',
    textAlign: 'center',
  },

  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '22px',
  },

  card: {
    padding: '26px',
    borderRadius: '16px',
    background: '#f8fafc',
    border: '1px solid #e2e8f0',
    textDecoration: 'none',
    color: '#020617',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 6px 18px rgba(0,0,0,0.06)',
  },

  cardHover: {
    transform: 'translateY(-8px)',
    background: '#ecfeff',
    border: '1px solid #38bdf8',
    boxShadow: '0 16px 40px rgba(56, 189, 248, 0.45)',
  },
};
