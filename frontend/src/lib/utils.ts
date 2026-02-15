import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function stripHtml(html: string) {
  if (!html) return '';
  // Simple regex to strip HTML tags
  return html.replace(/<[^>]*>?/gm, '').trim();
}
