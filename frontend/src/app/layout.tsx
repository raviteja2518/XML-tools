import Navbar from '@/components/Navbar';
import './globals.css';

export const metadata = {
  title: 'XML Tools',
  description: 'Professional PDF to XML & EPUB Tools',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
