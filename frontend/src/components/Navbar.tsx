'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { User } from 'lucide-react';

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const { user, logout, loading } = useAuth();

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

        {!isMobile && user && (
          <ul style={styles.links}>
            <NavLinks />
          </ul>
        )}

        {!isMobile && (
          <div style={styles.actions}>
            {!loading && (
              <>
                {!user ? (
                  <Link href="/login">
                    <button style={styles.login}>Login</button>
                  </Link>
                ) : (
                  <>
                    {user.role === 'admin' && (
                      <Link href="/admin">
                        <button style={styles.dashboard}>Admin Panel</button>
                      </Link>
                    )}

                    {/* Profile Link */}
                    <Link
                      href="/profile"
                      className="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-xs font-medium hover:bg-white/10 transition-all text-gray-300 hover:text-white"
                    >
                      <User className="w-3.5 h-3.5" />
                      Profile
                    </Link>
                    
                    <button style={styles.login} onClick={logout}>
                      Logout ({user.name})
                    </button>
                  </>
                )}
              </>
            )}
          </div>
        )}

        {isMobile && (
          <div style={styles.hamburger} onClick={() => setOpen(!open)}>
            ☰
          </div>
        )}
      </nav>

      {isMobile && open && (
        <div style={styles.mobileMenu}>
          {user && (
            <ul style={styles.mobileLinks}>
              <NavLinks onClick={() => setOpen(false)} />
            </ul>
          )}

          <div style={styles.mobileActions}>
            {!loading && (
              <>
                {!user ? (
                  <Link href="/login">
                    <button style={styles.login} onClick={() => setOpen(false)}>Login</button>
                  </Link>
                ) : (
                  <>
                    {user.role === 'admin' && (
                      <Link href="/admin">
                        <button style={styles.dashboard} onClick={() => setOpen(false)}>Admin Panel</button>
                      </Link>
                    )}
                    <Link href="/">
                      <button style={styles.dashboard} onClick={() => setOpen(false)}>Hub</button>
                    </Link>

                    {/* Profile Link */}
                    <Link
                      href="/profile"
                      className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full text-sm font-medium hover:bg-white/10 transition-all text-gray-300 hover:text-white"
                      onClick={() => setOpen(false)}
                    >
                      <User className="w-4 h-4" />
                      Profile
                    </Link>

                    <button style={styles.login} onClick={() => { logout(); setOpen(false); }}>
                      Logout ({user.name})
                    </button>
                  </>
                )}
              </>
            )}
          </div>

        </div>
      )}
    </>
  );
}

/* ---------- LINKS ---------- */
function NavLinks({ onClick }: { onClick?: () => void }) {
  const commonLinkStyle = {
    color: '#fff',
    textDecoration: 'none',
    transition: 'color 0.2s',
    cursor: 'pointer',
  };

  return (
    <>
      <li><Link href="/pdf-to-xml" onClick={onClick} style={commonLinkStyle}>PDF → XML</Link></li>
      <li><Link href="/ocr" onClick={onClick} style={commonLinkStyle}>OCR</Link></li>
      <li><Link href="/pdf-to-tiff" onClick={onClick} style={commonLinkStyle}>PDF → TIFF</Link></li>
      <li><Link href="/pdf-split" onClick={onClick} style={commonLinkStyle}>PDF Split</Link></li>
      <li><Link href="/epub2" onClick={onClick} style={commonLinkStyle}>EPUB2</Link></li>
      <li><Link href="/epub3" onClick={onClick} style={commonLinkStyle}>EPUB3</Link></li>
      <li><Link href="/Tools" onClick={onClick} style={commonLinkStyle}>Tools</Link></li>
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
