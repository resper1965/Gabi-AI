/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /contexts/NodeDataContext.tsx                                         │
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

/* eslint-disable @typescript-eslint/no-explicit-any */
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

interface NodeData {
  [key: string]: any;
}

interface NodeUploads {
  [key: string]: any;
}

interface NodeDataContextProps {
  nodeData: NodeData;
  setNodeData: React.Dispatch<React.SetStateAction<NodeData>>;
  showEdgeDeleteLabel: boolean;
  setShowEdgeDeleteLabel: React.Dispatch<React.SetStateAction<boolean>>;
  nodeUploads: NodeUploads;
  setNodeUploads: React.Dispatch<React.SetStateAction<NodeUploads>>;
  showUploadModal: boolean;
  setShowUploadModal: React.Dispatch<React.SetStateAction<boolean>>;
  currentUploadModalId: string | null;
  setCurrentUploadModalId: React.Dispatch<React.SetStateAction<string | null>>;
  currentUploadType: string;
  setCurrentUploadType: React.Dispatch<React.SetStateAction<string>>;
}

const NodeDataContext = createContext<NodeDataContextProps | undefined>(
  undefined,
);

// eslint-disable-next-line react-refresh/only-export-components
export const useNodeData = () => {
  const context = useContext(NodeDataContext);
  if (!context) {
    throw new Error("useNodeData must be used within a NodeDataProvider");
  }
  return context;
};

interface NodeDataProviderProps {
  children: ReactNode;
}

export const NodeDataProvider: React.FC<NodeDataProviderProps> = ({
  children,
}) => {
  const [nodeData, setNodeData] = useState<NodeData>({});
  const [nodeUploads, setNodeUploads] = useState<NodeUploads>({});

  const [showEdgeDeleteLabel, setShowEdgeDeleteLabel] =
    useState<boolean>(false);
  const [showUploadModal, setShowUploadModal] = useState<boolean>(false);
  const [currentUploadModalId, setCurrentUploadModalId] = useState<
    string | null
  >(null);
  const [currentUploadType, setCurrentUploadType] = useState<string>("image");

  useEffect(() => {
    // You can add logic here if needed
  }, [nodeData]);

  return (
    <NodeDataContext.Provider
      value={{
        nodeData,
        setNodeData,
        showEdgeDeleteLabel,
        setShowEdgeDeleteLabel,
        nodeUploads,
        setNodeUploads,
        showUploadModal,
        setShowUploadModal,
        currentUploadModalId,
        setCurrentUploadModalId,
        currentUploadType,
        setCurrentUploadType,
      }}
    >
      {children}
    </NodeDataContext.Provider>
  );
};
