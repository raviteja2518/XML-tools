import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const publicPaths = ['/login', '/register'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const { pathname } = request.nextUrl;

  const protectedRoutes = [
    '/admin', 
    '/profile', 
    '/payment',
    '/pdf-to-xml', 
    '/ocr', 
    '/pdf-to-tiff', 
    '/pdf-split', 
    '/epub2', 
    '/epub3', 
    '/Tools', 
    '/pdf-to-word', 
    '/xml-editor', 
    '/ocr-docbook'
  ];
  const authRoutes = ['/login', '/register'];

  const isAuthRoute = authRoutes.includes(pathname);
  const isHomePage = pathname === '/';
  const isPublicRoute = isAuthRoute || isHomePage;

  // 1. If user is logged in and tries to access login/register, send to home
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  // 2. If user is NOT logged in and tries to access anything other than public routes, send to login
  if (!isPublicRoute && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
