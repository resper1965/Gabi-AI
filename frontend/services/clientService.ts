/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /services/clientService.ts                                            │
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

export interface Client {
  id: string;
  name: string;
  email: string;
  created_at: string;
  users_count?: number;
  agents_count?: number;
}

export interface CreateClientRequest {
  name: string;
  email: string;
  password: string;
}

export interface UpdateClientRequest {
  name: string;
  email: string;
}

export interface ListClientsResponse {
  items: Client[];
  total: number;
}

export const createClient = async (client: any) => {
  try {
    const response = await api.post("/api/v1/clients", client);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const listClients = (skip = 0, limit = 10) =>
  api.get<Client[]>(`/api/v1/clients/?skip=${skip}&limit=${limit}`);
export const getClient = (clientId: string) =>
  api.get<Client>(`/api/v1/clients/${clientId}`);
export const updateClient = (clientId: string, data: UpdateClientRequest) =>
  api.put<Client>(`/api/v1/clients/${clientId}`, data);
export const deleteClient = async (id: string) => {
  try {
    const response = await api.delete(`/api/v1/clients/${id}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const impersonateClient = async (id: string) => {
  try {
    const response = await api.post(`/api/v1/clients/${id}/impersonate`);
    return response.data;
  } catch (error) {
    throw error;
  }
};
