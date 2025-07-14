/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /app/security/verify-email/page.tsx                                   │
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
"use client"

import { useEffect, useState, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Loader2, CheckCircle2, XCircle } from "lucide-react"
import { verifyEmail } from "@/services/authService"

export default function VerifyEmailPageWrapper() {
    return (
        <Suspense fallback={null}>
            <VerifyEmailPage />
        </Suspense>
    )
}

function VerifyEmailPage() {
    const searchParams = useSearchParams()
    const router = useRouter()
    const code = searchParams.get("code")
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle")
    const [error, setError] = useState<string | null>(null)
    const [redirectSeconds, setRedirectSeconds] = useState(5)

    useEffect(() => {
        if (!code) {
            setError("Verification code not found in URL.")
            setStatus("error")
            return
        }
        setStatus("loading")
        verifyEmail(code)
            .then(() => {
                setStatus("success")
            })
            .catch((err) => {
                setError(err?.response?.data?.message || "Failed to verify email.")
                setStatus("error")
            })
    }, [code])

    useEffect(() => {
        if (status === "success" && redirectSeconds > 0) {
            const timer = setTimeout(() => {
                setRedirectSeconds((s) => s - 1)
            }, 1000)
            return () => clearTimeout(timer)
        }
        if (status === "success" && redirectSeconds === 0) {
            router.push("/login")
        }
    }, [status, redirectSeconds, router])

    return (
        <div className="flex min-h-screen items-center justify-center bg-background">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle>Email Confirmation</CardTitle>
                </CardHeader>
                <CardContent>
                    {status === "loading" && (
                        <Alert>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                            <AlertTitle>Verifying your email...</AlertTitle>
                        </Alert>
                    )}
                    {status === "success" && (
                        <Alert className="border-green-500">
                            <CheckCircle2 className="mr-2 h-4 w-4 text-green-500 inline" />
                            <AlertTitle>Email verified!</AlertTitle>
                            <AlertDescription>
                                Your email has been successfully confirmed.<br />
                                Redirecting to login in {redirectSeconds} seconds...
                            </AlertDescription>
                        </Alert>
                    )}
                    {status === "error" && (
                        <Alert variant="destructive">
                            <XCircle className="mr-2 h-4 w-4 inline" />
                            <AlertTitle>Verification failed</AlertTitle>
                            <AlertDescription>
                                {error || "An error occurred while verifying your email."}
                            </AlertDescription>
                        </Alert>
                    )}
                </CardContent>
            </Card>
        </div>
    )
} 