/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: /lib/file-utils.ts                                                    │
│ Developed by: Davidson Gomes                                                 │
│ Creation date: August 24, 2025                                               │
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

export interface FileData {
  filename: string;
  content_type: string;
  data: string;
  size: number;
  preview_url?: string;
}

export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64 = reader.result as string;
      const base64Data = base64.split(',')[1];
      resolve(base64Data);
    };
    reader.onerror = error => reject(error);
  });
}

export async function fileToFileData(file: File): Promise<FileData> {
  const base64Data = await fileToBase64(file);
  const previewUrl = URL.createObjectURL(file);
  
  return {
    filename: file.name,
    content_type: file.type,
    data: base64Data,
    size: file.size,
    preview_url: previewUrl
  };
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) {
    return '0 Bytes';
  }
  
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
}

export function isImageFile(mimeType: string): boolean {
  return mimeType.startsWith('image/');
}

export function isPdfFile(mimeType: string): boolean {
  return mimeType === 'application/pdf';
}

export function getFileIcon(mimeType: string): string {
  if (isImageFile(mimeType)) {
    return 'image';
  }
  if (isPdfFile(mimeType)) {
    return 'file-text';
  }
  if (mimeType.includes('word')) {
    return 'file-text';
  }
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) {
    return 'file-spreadsheet';
  }
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) {
    return 'file-presentation';
  }
  if (mimeType.includes('text/')) {
    return 'file-text';
  }
  if (mimeType.includes('audio/')) {
    return 'file-audio';
  }
  if (mimeType.includes('video/')) {
    return 'file-video';
  }
  
  return 'file';
} 