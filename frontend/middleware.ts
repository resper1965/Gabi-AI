/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /middleware.ts                                                        │
│ Developed by: Davidson Gomes                                                 │
│ Creation date: May 13, 2025                                                  │
│ Contact: contato@evolution-api.com                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ @copyright © Evolution API 2025. All rights reserved.                        │
│ Licensed under the Apache License, Version 2.0                               │
│                                                                              │
│ You may not use this file except in compliance with the License.             │
│ You may obtain a copy of the License at                                      │
│                                                                              │
│    http://www.apache.org/licenses/LICENSE-2.0                                │
│                                                                              │
│ Unless required by applicable law or agreed to in writing, software          │
│ distributed under the License is distributed on an "AS IS" BASIS,            │
│ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.     │
│ See the License for the specific language governing permissions and          │
│ limitations under the License.                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ @important                                                                   │
│ For any future changes to the code in this file, it is recommended to        │
│ include, together with the modification, the information of the developer    │
│ who changed it and the date of modification.                                 │
└──────────────────────────────────────────────────────────────────────────────┘
*/
import { NextRequest, NextResponse } from 'next/server'

const PUBLIC_PATHS = ['/login', '/security/verify-email', '/security/reset-password', '/shared-chat']
const ADMIN_PATHS = ['/clients', '/mcp-servers']
const CLIENT_PATHS = ['/agents', '/chat']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isPublic = PUBLIC_PATHS.some((path) => pathname.startsWith(path))
  const isAdminPath = ADMIN_PATHS.some((path) => pathname.startsWith(path))
  const isClientPath = CLIENT_PATHS.some((path) => pathname.startsWith(path))

  const token = request.cookies.get('access_token')?.value
  let isAdmin = false
  let isImpersonating = false
  
  const userCookie = request.cookies.get('user')?.value
  if (userCookie) {
    try {
      const user = JSON.parse(decodeURIComponent(userCookie))
      isAdmin = !!user.is_admin
    } catch {}
  }
  
  isImpersonating = request.cookies.get('isImpersonating')?.value === 'true'
  
  if (!isImpersonating) {
    const headers = request.headers
    isImpersonating = headers.get('x-is-impersonating') === 'true'
  }

  if (isPublic && token) {
    if (pathname.startsWith('/shared-chat')) {
      return NextResponse.next()
    }
    return NextResponse.redirect(new URL('/', request.url))
  }

  if (!isPublic && !token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  if (isAdminPath && !isAdmin) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  if (isClientPath && isAdmin && !isImpersonating) {
    return NextResponse.redirect(new URL('/mcp-servers', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.svg).*)'],
} 