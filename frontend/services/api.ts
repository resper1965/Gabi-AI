/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /services/api.ts                                                      │
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
import axios from "axios";
import { getApiUrl } from "@/lib/env";

const apiUrl = getApiUrl();

const api = axios.create({
  baseURL: apiUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

// Flag to prevent multiple logout attempts
let isLoggingOut = false;

// Function to force logout
const forceLogout = () => {
  if (isLoggingOut) return;
  isLoggingOut = true;

  // Clear localStorage
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
  localStorage.removeItem("impersonatedClient");
  localStorage.removeItem("isImpersonating");

  // Clear cookies
  document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  document.cookie = "user=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  document.cookie = "impersonatedClient=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  document.cookie = "isImpersonating=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  
  // Redirect to login page
  window.location.href = "/login?session_expired=true";
};

// Interceptor to add the token from the cookie to the Authorization header
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    // Verificar primeiro se estamos em uma rota de agente compartilhado
    const isSharedAgentRequest = config.url && (
      config.url.includes('/agents/shared') || 
      config.url.includes('/chat/ws/')
    );

    const isSharedChatPage = typeof window !== "undefined" && 
      window.location.pathname.startsWith('/shared-chat');

    // Usar API key apenas para requisições específicas de agentes compartilhados ou na página de chat compartilhado
    if ((isSharedAgentRequest || isSharedChatPage) && localStorage.getItem("shared_agent_api_key")) {
      const apiKey = localStorage.getItem("shared_agent_api_key");
      config.headers = config.headers || {};
      config.headers["x-api-key"] = apiKey;
    } else {
      // Caso contrário, usar a autenticação normal com JWT
      const match = document.cookie.match(/(?:^|; )access_token=([^;]*)/);
      const token = match ? decodeURIComponent(match[1]) : null;
      if (token) {
        config.headers = config.headers || {};
        config.headers["Authorization"] = `Bearer ${token}`;
      }
    }
  }
  return config;
});

// Interceptor to handle 401 Unauthorized responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Check if we have a 401 Unauthorized error and we're in a browser context
    if (error.response && error.response.status === 401 && typeof window !== "undefined") {
      // Skip logout for login endpoint and other auth endpoints
      const isAuthEndpoint = error.config.url && (
        error.config.url.includes('/auth/login') || 
        error.config.url.includes('/auth/register') ||
        error.config.url.includes('/auth/forgot-password') ||
        error.config.url.includes('/auth/reset-password')
      );

      // Skip logout for shared chat page
      const isSharedChatPage = typeof window !== "undefined" && 
        window.location.pathname.startsWith('/shared-chat');

      if (!isAuthEndpoint && !isSharedChatPage) {
        forceLogout();
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
