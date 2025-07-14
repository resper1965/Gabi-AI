/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @author: Victor Calazans - Implementation of Delay node type                 │
│ @file: /app/agents/workflows/nodes/index.ts                                  │
│ Developed by: Davidson Gomes                                                 │
│ Delay node functionality developed by: Victor Calazans                       │
│ Creation date: May 13, 2025                                                  │
│ Delay implementation date: May 17, 2025                                      │
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
import type { NodeTypes, BuiltInNode, Node } from "@xyflow/react";

import { ConditionNode } from "./components/condition/ConditionNode";
import { AgentNode } from "./components/agent/AgentNode";
import { StartNode, StartNodeType } from "./components/start/StartNode";
import { MessageNode } from "./components/message/MessageNode";
import { DelayNode } from "./components/delay/DelayNode";

import "./style.css";
import {
  ConditionType,
  MessageType,
  DelayType,
} from "./nodeFunctions";
import { Agent } from "@/types/agent";

type AgentNodeType = Node<
  {
    label?: string;
    agent?: Agent;
  },
  "agent-node"
>;

type MessageNodeType = Node<
  {
    label?: string;
    message?: MessageType;
  },
  "message-node"
>;

type DelayNodeType = Node<
  {
    label?: string;
    delay?: DelayType;
  },
  "delay-node"
>;

type ConditionNodeType = Node<
  {
    label?: string;
    integration?: string;
    icon?: string;
    conditions?: ConditionType[];
  },
  "condition-node"
>;

export type AppNode =
  | BuiltInNode
  | StartNodeType
  | AgentNodeType
  | ConditionNodeType
  | MessageNodeType
  | DelayNodeType;

export type NodeType = AppNode["type"];

export const initialNodes: AppNode[] = [
  {
    id: "start-node",
    type: "start-node",
    position: { x: -100, y: 100 },
    data: {
      label: "Start",
    },
  },
];

export const nodeTypes = {
  "start-node": StartNode,
  "agent-node": AgentNode,
  "message-node": MessageNode,
  "condition-node": ConditionNode,
  "delay-node": DelayNode,
} satisfies NodeTypes;
