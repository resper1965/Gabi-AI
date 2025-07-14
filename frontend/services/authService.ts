/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /services/authService.ts                                              │
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
import api from "./api";
import {
  RegisterRequest,
  RegisterResponse,
  LoginRequest,
  LoginResponse,
  ResendVerificationRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  MeResponse,
  ChangePasswordRequest,
} from "../types/auth";

export const register = (data: RegisterRequest) =>
  api.post<RegisterResponse>("/api/v1/auth/register", data);
export const login = (data: LoginRequest) =>
  api.post<LoginResponse>("/api/v1/auth/login", data);
export const verifyEmail = (code: string) =>
  api.get(`/api/v1/auth/verify-email/${code}`);
export const resendVerification = (data: ResendVerificationRequest) =>
  api.post("/api/v1/auth/resend-verification", data);
export const forgotPassword = (data: ForgotPasswordRequest) =>
  api.post("/api/v1/auth/forgot-password", data);
export const resetPassword = (data: ResetPasswordRequest) =>
  api.post("/api/v1/auth/reset-password", data);
export const getMe = () => api.post<MeResponse>("/api/v1/auth/me");
export const changePassword = (data: ChangePasswordRequest) =>
  api.post("/api/v1/auth/change-password", data);
