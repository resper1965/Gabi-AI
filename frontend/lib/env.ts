import { env } from 'next-runtime-env';

export const getEnv = (key: string, defaultValue?: string): string => {
  try {
    const value = env(key);
    return value || defaultValue || '';
  } catch (error) {
    console.error(`Error getting environment variable ${key}:`, error);
    return defaultValue || '';
  }
};

export const getApiUrl = (): string => {
  return getEnv('NEXT_PUBLIC_API_URL', 'https://api-evoai.evoapicloud.com');
}; 