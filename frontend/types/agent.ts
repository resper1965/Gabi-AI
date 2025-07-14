/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /types/agent.ts                                                       │
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
export type AgentType =
  | "llm"
  | "a2a"
  | "sequential"
  | "parallel"
  | "loop"
  | "workflow"
  | "task";

export interface ToolConfig {
  id: string;
  envs: Record<string, string>;
}

export interface MCPServerConfig {
  id: string;
  envs: Record<string, string>;
  tools: string[];
  selected_tools?: string[];
}

export interface CustomMCPServer {
  url: string;
  headers?: Record<string, string>;
}

export interface HTTPToolParameter {
  type: string;
  required: boolean;
  description: string;
}

export interface HTTPToolParameters {
  path_params?: Record<string, string>;
  query_params?: Record<string, string | string[]>;
  body_params?: Record<string, HTTPToolParameter>;
}

export interface HTTPToolErrorHandling {
  timeout: number;
  retry_count: number;
  fallback_response: Record<string, string>;
}

export interface HTTPTool {
  name: string;
  method: string;
  values: Record<string, string>;
  headers: Record<string, string>;
  endpoint: string;
  parameters: HTTPToolParameters;
  description: string;
  error_handling: HTTPToolErrorHandling;
}

export interface CustomTools {
  http_tools: HTTPTool[];
}

export interface WorkflowData {
  nodes: any[];
  edges: any[];
}

export interface TaskConfig {
  agent_id: string;
  description: string;
  expected_output: string;
  enabled_tools?: string[];
}

export interface AgentConfig {
  // LLM config
  api_key?: string;
  tools?: ToolConfig[];
  custom_tools?: CustomTools;
  mcp_servers?: MCPServerConfig[];
  custom_mcp_servers?: CustomMCPServer[];

  // Sequential, Parallel e Loop config
  sub_agents?: string[];
  agent_tools?: string[];

  // Loop config
  max_iterations?: number;

  // Workflow config
  workflow?: WorkflowData;

  // Task config
  tasks?: TaskConfig[];
}

export interface Agent {
  id: string;
  client_id: string;
  folder_id?: string;
  name: string;
  description?: string;
  role?: string;
  goal?: string;
  type: AgentType;
  model?: string;
  api_key_id?: string;
  instruction?: string;
  agent_card_url?: string;
  config?: AgentConfig;
  tasks?: TaskConfig[];
  created_at: string;
  updated_at?: string;
}

export interface AgentCreate {
  client_id: string;
  name: string;
  description?: string;
  role?: string;
  goal?: string;
  type: AgentType;
  model?: string;
  api_key_id?: string;
  instruction?: string;
  agent_card_url?: string;
  config?: AgentConfig;
}
