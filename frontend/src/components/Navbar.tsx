'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // ✅ Client-only width check (hydration safe)
  useEffect(() => {
    const checkScreen = () => setIsMobile(window.innerWidth < 900);
    checkScreen();
    window.addEventListener('resize', checkScreen);
    return () => window.removeEventListener('resize', checkScreen);
  }, []);

  return (
    <>
      <nav style={styles.navbar}>
        <div style={styles.logo}>XML Tools</div>

        {!isMobile && (
          <>
            <ul style={styles.links}>
              <NavLinks />
            </ul>

            <div style={styles.mobileActions}>
  <Link href="/login">
    <button style={styles.login}>Login</button>
  </Link>

  <Link href="/">
    <button style={styles.dashboard}>Dashboard</button>
  </Link>
</div>

          </>
        )}

        {isMobile && (
          <div style={styles.hamburger} onClick={() => setOpen(!open)}>
            ☰
          </div>
        )}
      </nav>

      {isMobile && open && (
        <div style={styles.mobileMenu}>
          <ul style={styles.mobileLinks}>
            <NavLinks onClick={() => setOpen(false)} />
          </ul>

          <div style={styles.mobileActions}>
  <Link href="/login">
    <button style={styles.login}>Login</button>
  </Link>

  <Link href="/">
    <button style={styles.dashboard}>Dashboard</button>
  </Link>
</div>

        </div>
      )}
    </>
  );
}

/* ---------- LINKS ---------- */
function NavLinks({ onClick }: { onClick?: () => void }) {
  return (
    <>
      <li><Link href="/pdf-to-xml" onClick={onClick}>PDF → XML</Link></li>
      <li><Link href="/pdf-to-word" onClick={onClick}>PDF → Word</Link></li>
      <li><Link href="/ocr" onClick={onClick}>OCR</Link></li>
      <li><Link href="/pdf-to-tiff" onClick={onClick}>PDF → TIFF</Link></li>
      <li><Link href="/pdf-split" onClick={onClick}>PDF Split</Link></li>
      <li><Link href="/epub2" onClick={onClick}>EPUB2</Link></li>
      <li><Link href="/epub3" onClick={onClick}>EPUB3</Link></li>
      <li><Link href="/Tools" onClick={onClick}>Tools</Link></li>
    </>
  );
}

/* ---------- STYLES ---------- */
const styles: any = {
  navbar: {
    position: 'sticky',
    top: 0,
    zIndex: 1000,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '14px 24px',
    background: '#0f172a',
    color: '#fff',
  },
  logo: {
    fontSize: '22px',
    fontWeight: 'bold',
  },
  links: {
    display: 'flex',
    gap: '18px',
    listStyle: 'none',
    fontSize: '14px',
  },
  actions: {
    display: 'flex',
    gap: '10px',
  },
  login: {
    background: '#38bdf8',
    color: '#fff',
    border: '1px solid #38bdf8',
    padding: '6px 12px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  dashboard: {
    background: '#38bdf8',
    border: 'none',
    padding: '6px 14px',
    borderRadius: '6px',
    fontWeight: 'bold',
    cursor: 'pointer',
  },
  hamburger: {
    fontSize: '28px',
    cursor: 'pointer',
  },
  mobileMenu: {
    background: 'white',
    padding: '20px',
  },
  mobileLinks: {
    listStyle: 'none',
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  mobileActions: {
    marginTop: '20px',
    display: 'flex',
    gap: '10px',
  },
};
