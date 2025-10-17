import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function middleware(req: NextRequest) {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )

  const accessToken = req.cookies.get('sb-access-token')?.value

  if (!accessToken && !req.nextUrl.pathname.startsWith('/login')) {
    const redirectUrl = req.nextUrl.clone()
    redirectUrl.pathname = '/login'
    return NextResponse.redirect(redirectUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/', '/((?!_next|api|static|favicon.ico).*)'],
}
