/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /app/documentation/components/CodeBlock.tsx                           │
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
import React from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dracula } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { Button } from "@/components/ui/button";
import { ClipboardCopy } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface CodeBlockProps {
  text: string;
  language: string;
  showLineNumbers?: boolean;
}

export function CodeBlock({ text, language, showLineNumbers = true }: CodeBlockProps) {
  const { toast } = useToast();
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied!",
      description: "Code copied to clipboard",
    });
  };

  return (
    <div className="relative rounded-md overflow-hidden">
      <SyntaxHighlighter
        language={language}
        style={dracula}
        showLineNumbers={showLineNumbers}
        wrapLines={true}
        customStyle={{
          margin: 0,
          padding: "1rem",
          borderRadius: "0.375rem",
        }}
      >
        {text}
      </SyntaxHighlighter>
      <Button
        size="sm"
        variant="ghost"
        className="absolute top-2 right-2 text-white hover:bg-[#333] opacity-80 hover:opacity-100"
        onClick={copyToClipboard}
      >
        <ClipboardCopy className="h-4 w-4" />
      </Button>
    </div>
  );
} 