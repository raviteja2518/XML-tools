'use client';

import Link from 'next/link';

const COURTS = [
  { name: 'USA', slug: 'usa' },
  { name: 'Texas', slug: 'taxas' },
  { name: 'California', slug: 'california' },
  { name: 'Puerto Rico', slug: 'puerto_rico' },
  { name: 'Pennsylvania', slug: 'pennsylvania' },
  { name: 'Ohio', slug: 'ohio' },
  { name: 'New York', slug: 'newyork' },
  { name: 'Illinois', slug: 'illinois' },
  { name: 'General Case of Law', slug: 'general' },
  { name: 'Federal CT Superior', slug: 'federal_ct' },
  { name: 'FED Claims', slug: 'fed_claims' },
];

export default function CourtSelectionPage() {
  return (
    <div style={styles.page}>
      <h2 style={styles.title}>Court Case – LN XML Conversion</h2>
      <p style={styles.subtitle}>
        Select country / court type to convert court case PDFs into LN XML
      </p>

      <div style={styles.grid}>
        {COURTS.map(court => (
          <Link key={court.slug} href={`/pdf-to-xml/court/${court.slug}`}>
            <div style={styles.card}>
              <h3 style={styles.cardTitle}>{court.name}</h3>
              <p style={styles.cardDesc}>
                LN XML conversion for {court.name} court cases
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const styles: any = {
  page: {
    maxWidth: '1500px',
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
    padding: '26px',
    borderRadius: '14px',
    background: '#f8fafc',
    border: '1px solid #e2e8f0',
    cursor: 'pointer',
    transition: 'all 0.25s ease',
  },

  cardTitle: {
    fontSize: '18px',
    marginBottom: '10px',
    color: '#0f172a',
  },

  cardDesc: {
    fontSize: '14px',
    color: '#475569',
    lineHeight: '1.6',
  },
};
