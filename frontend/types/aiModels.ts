/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /types/aiModels.ts                                                    │
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
export const availableModels = [
  // GPT-4.1 series
  { value: "openai/gpt-4.1", label: "GPT-4.1", provider: "openai" },
  { value: "openai/gpt-4.1-nano", label: "GPT-4.1 Nano", provider: "openai" },
  { value: "openai/gpt-4.1-mini", label: "GPT-4.1 Mini", provider: "openai" },

  // GPT-4.5 Preview
  {
    value: "openai/gpt-4.5-preview",
    label: "GPT-4.5 Preview",
    provider: "openai",
  },

  // GPT-4 Turbo & GPT-4o
  { value: "openai/gpt-4", label: "GPT-4 Turbo", provider: "openai" },
  { value: "openai/gpt-4o", label: "GPT-4o", provider: "openai" },
  { value: "openai/gpt-4o-mini", label: "GPT-4o Mini", provider: "openai" },

  // GPT-4 Legacy
  { value: "openai/gpt-4-32k", label: "GPT-4 32K", provider: "openai" },

  // GPT-3.5 Turbo series
  {
    value: "openai/gpt-3.5-turbo",
    label: "GPT-3.5 Turbo",
    provider: "openai",
  },
  {
    value: "openai/gpt-3.5-turbo-16k",
    label: "GPT-3.5 Turbo 16K",
    provider: "openai",
  },

  // Gemini Preview models
  {
    value: "gemini/gemini-2.5-pro-preview-05-06",
    label: "Gemini 2.5 Pro (Preview)",
    provider: "gemini",
  },
  {
    value: "gemini/gemini-2.5-flash-preview-04-17",
    label: "Gemini 2.5 Flash (Preview)",
    provider: "gemini",
  },

  // Gemini GA models
  {
    value: "gemini/gemini-2.0-flash",
    label: "Gemini 2.0 Flash",
    provider: "gemini",
  },
  {
    value: "gemini/gemini-2.0-flash-lite",
    label: "Gemini 2.0 Flash-Lite",
    provider: "gemini",
  },
  {
    value: "gemini/gemini-2.0-flash-live-001",
    label: "Gemini 2.0 Flash Live",
    provider: "gemini",
  },

  // Gemini Legacy models
  {
    value: "gemini/gemini-1.5-pro",
    label: "Gemini 1.5 Pro",
    provider: "gemini",
  },
  {
    value: "gemini/gemini-1.5-flash",
    label: "Gemini 1.5 Flash",
    provider: "gemini",
  },
  {
    value: "gemini/gemini-1.5-flash-8b",
    label: "Gemini 1.5 Flash-8B",
    provider: "gemini",
  },

  // Claude 3.7 models
  {
    value: "anthropic/claude-3-7-sonnet-20250219",
    label: "Claude 3.7 Sonnet",
    provider: "anthropic",
  },

  // Claude 3.5 models
  {
    value: "anthropic/claude-3-5-sonnet-20241022",
    label: "Claude 3.5 Sonnet v2",
    provider: "anthropic",
  },
  {
    value: "anthropic/claude-3-5-sonnet-20240620",
    label: "Claude 3.5 Sonnet",
    provider: "anthropic",
  },
  {
    value: "anthropic/claude-3-5-haiku-20241022",
    label: "Claude 3.5 Haiku",
    provider: "anthropic",
  },

  // Claude 3 models
  {
    value: "anthropic/claude-3-opus-20240229",
    label: "Claude 3 Opus",
    provider: "anthropic",
  },
  {
    value: "anthropic/claude-3-sonnet-20240229",
    label: "Claude 3 Sonnet",
    provider: "anthropic",
  },
  {
    value: "anthropic/claude-3-haiku-20240307",
    label: "Claude 3 Haiku",
    provider: "anthropic",
  },

  // Groq Production Models
  {
    value: "groq/gemma2-9b-it",
    label: "Gemma2 9B-IT (Google)",
    provider: "groq",
  },
  {
    value: "groq/llama-3.3-70b-versatile",
    label: "Llama 3.3 70B Versatile (Meta)",
    provider: "groq",
  },
  {
    value: "groq/llama-3.1-8b-instant",
    label: "Llama 3.1 8B Instant (Meta)",
    provider: "groq",
  },
  {
    value: "groq/llama-guard-3-8b",
    label: "Llama Guard 3 8B (Meta)",
    provider: "groq",
  },
  {
    value: "groq/llama3-70b-8192",
    label: "Llama3 70B (Meta)",
    provider: "groq",
  },
  {
    value: "groq/llama3-8b-8192",
    label: "Llama3 8B (Meta)",
    provider: "groq",
  },
  {
    value: "groq/whisper-large-v3",
    label: "Whisper Large v3 (OpenAI)",
    provider: "groq",
  },
  {
    value: "groq/whisper-large-v3-turbo",
    label: "Whisper Large v3 Turbo (OpenAI)",
    provider: "groq",
  },
  {
    value: "groq/distil-whisper-large-v3-en",
    label: "Distil Whisper Large v3-EN (HuggingFace)",
    provider: "groq",
  },

  // Groq Preview Models
  {
    value: "groq/allam-2-7b",
    label: "Allam 2 7B (SDAIA)",
    provider: "groq",
  },
  {
    value: "groq/deepseek-r1-distill-llama-70b",
    label: "DeepSeek R1 Distill Llama 70B",
    provider: "groq",
  },
  {
    value: "groq/meta-llama-llama-4-maverick-17b-128e-instruct",
    label: "Llama 4 Maverick 17B Instruct (Meta)",
    provider: "groq",
  },

  // Groq Preview Systems
  {
    value: "groq/compound-beta",
    label: "Compound Beta",
    provider: "groq",
  },
  {
    value: "groq/compound-beta-mini",
    label: "Compound Beta Mini",
    provider: "groq",
  },

  // Cohere Command Family
  {
    value: "cohere/command-a-03-2025",
    label: "Command A (256K context)",
    provider: "cohere",
  },
  {
    value: "cohere/command-r7b-12-2024",
    label: "Command R7B (128K context)",
    provider: "cohere",
  },
  {
    value: "cohere/command-r-plus-08-2024",
    label: "Command R+ (128K context)",
    provider: "cohere",
  },
  {
    value: "cohere/command-r-08-2024",
    label: "Command R (128K context)",
    provider: "cohere",
  },

  // Cohere Embed Family
  {
    value: "cohere/embed-v4.0",
    label: "Embed v4.0 (Multimodal)",
    provider: "cohere",
  },
  {
    value: "cohere/embed-english-v3.0",
    label: "Embed English v3.0",
    provider: "cohere",
  },
  {
    value: "cohere/embed-english-light-v3.0",
    label: "Embed English Light v3.0",
    provider: "cohere",
  },
  {
    value: "cohere/embed-multilingual-v3.0",
    label: "Embed Multilingual v3.0",
    provider: "cohere",
  },
  {
    value: "cohere/embed-multilingual-light-v3.0",
    label: "Embed Multilingual Light v3.0",
    provider: "cohere",
  },

  // Cohere Rerank Family
  {
    value: "cohere/rerank-v3.5",
    label: "Rerank v3.5 (Multilingual)",
    provider: "cohere",
  },
  {
    value: "cohere/rerank-english-v3.0",
    label: "Rerank English v3.0",
    provider: "cohere",
  },
  {
    value: "cohere/rerank-multilingual-v3.0",
    label: "Rerank Multilingual v3.0",
    provider: "cohere",
  },

  // Cohere Aya Family
  {
    value: "cohere/c4ai-aya-expanse-8b",
    label: "Aya Expanse 8B (23 languages)",
    provider: "cohere",
  },
  {
    value: "cohere/c4ai-aya-expanse-32b",
    label: "Aya Expanse 32B (128K context)",
    provider: "cohere",
  },
  {
    value: "cohere/c4ai-aya-vision-8b",
    label: "Aya Vision 8B (Multimodal)",
    provider: "cohere",
  },
  {
    value: "cohere/c4ai-aya-vision-32b",
    label: "Aya Vision 32B (Multimodal)",
    provider: "cohere",
  },

  // Mistral Premier Models
  {
    value: "mistral/mistral-large-2-v24.11",
    label: "Mistral Large 2 (123B, 128K context)",
    provider: "mistral",
  },
  {
    value: "mistral/pixtral-large-v24.11",
    label: "Pixtral Large (Multimodal, 128K context)",
    provider: "mistral",
  },
  {
    value: "mistral/mistral-medium-3-v07.05",
    label: "Mistral Medium 3 (128K context)",
    provider: "mistral",
  },
  {
    value: "mistral/mistral-saba-v25.02",
    label: "Mistral Saba (Middle East & South Asia, 32K context)",
    provider: "mistral",
  },
  {
    value: "mistral/ministral-8b-v24.10",
    label: "Ministral 8B (128K context)",
    provider: "mistral",
  },
  {
    value: "mistral/ministral-3b-v24.10",
    label: "Ministral 3B (128K context)",
    provider: "mistral",
  },
  {
    value: "mistral/mistral-small-3.1-v25.03",
    label: "Mistral Small 3.1 (24B, Multimodal)",
    provider: "mistral",
  },

  // Mistral Open-Source Models
  {
    value: "mistral/mistral-7b",
    label: "Mistral 7B (128K context)",
    provider: "mistral",
  },
  {
    value: "mistral/mixtral-8x7b",
    label: "Mixtral 8×7B (MoE, 128K context)",
    provider: "mistral",
  },
  {
    value: "mistral/mixtral-8x22b",
    label: "Mixtral 8×22B (MoE, 128K context)",
    provider: "mistral",
  },
  {
    value: "mistral/codestral-mamba-7b",
    label: "Codestral Mamba 7B (Code, 128K context)",
    provider: "mistral",
  },
  {
    value: "mistral/codestral-22b",
    label: "Codestral 22B (Code, non-commercial)",
    provider: "mistral",
  },
  {
    value: "mistral/mathstral-7b",
    label: "Mathstral 7B (STEM, 32K context)",
    provider: "mistral",
  },
  {
    value: "mistral/mistral-nemo",
    label: "Mistral Nemo (Code focus)",
    provider: "mistral",
  },
  {
    value: "mistral/pixtral-12b",
    label: "Pixtral 12B (Multimodal, 128K context)",
    provider: "mistral",
  },
];

export const availableModelProviders = [
  {
    value: "openai",
    label: "OpenAI",
  },
  {
    value: "gemini",
    label: "Gemini",
  },
  {
    value: "anthropic",
    label: "Anthropic",
  },
  {
    value: "groq",
    label: "Groq",
  },
  {
    value: "cohere",
    label: "Cohere",
  },
];
