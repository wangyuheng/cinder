import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const PUBLIC_PATHS = [
  '/onboarding',
  '/api/health',
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  if (PUBLIC_PATHS.some(path => pathname.startsWith(path))) {
    return NextResponse.next()
  }

  if (pathname.startsWith('/_next') || pathname.startsWith('/static')) {
    return NextResponse.next()
  }

  const sessionId = request.cookies.get('session_id')

  if (!sessionId) {
    return NextResponse.redirect(new URL('/onboarding/invitation', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}
