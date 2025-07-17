/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /services/mcpServerService.ts                                         │
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
import { MCPServer, MCPServerCreate } from "../types/mcpServer";

export const createMCPServer = (data: MCPServerCreate) =>
  api.post<MCPServer>("/api/v1/mcp-servers/", data);

export const listMCPServers = (skip = 0, limit = 100) =>
  api.get<MCPServer[]>(`/api/v1/mcp-servers/?skip=${skip}&limit=${limit}`);

export const getMCPServer = (id: string) =>
  api.get<MCPServer>(`/api/v1/mcp-servers/${id}`);

export const updateMCPServer = (id: string, data: MCPServerCreate) =>
  api.put<MCPServer>(`/api/v1/mcp-servers/${id}`, data);

export const deleteMCPServer = (id: string) =>
  api.delete(`/api/v1/mcp-servers/${id}`);
