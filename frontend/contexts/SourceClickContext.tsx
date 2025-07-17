/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /contexts/SourceClickContext.tsx                                      │
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
"use client";

import { Node } from "@xyflow/react";
import React, { createContext, useState, useContext } from "react";

interface SourceClickContextProps {
  sourceClicked: Node | null;
  setSourceClicked: React.Dispatch<React.SetStateAction<Node | null>>;
}

const SourceClickContext = createContext<SourceClickContextProps | undefined>(
  undefined,
);

export const useSourceClick = () => {
  const context = useContext(SourceClickContext);
  if (!context) {
    throw new Error("useSourceClick must be used within a SourceClickProvider");
  }
  return context;
};

interface SourceClickProviderProps {
  children: React.ReactNode;
}

export const SourceClickProvider: React.FC<SourceClickProviderProps> = ({
  children,
}) => {
  const [sourceClicked, setSourceClicked] = useState<Node | null>(null);

  return (
    <SourceClickContext.Provider value={{ sourceClicked, setSourceClicked }}>
      {children}
    </SourceClickContext.Provider>
  );
};
