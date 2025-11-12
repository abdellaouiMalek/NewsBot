import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { ArticleQueryParams } from "./api/schemas/article.schema"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


/**
 * Utility: convert to FastAPI-compatible query params
 */
export function toFastApiParams(params: ArticleQueryParams) {
  return {
    page: params.page,
    page_size: params.page_size,
    category: params.category,
    source_name: params.source_name,
    fetch_method: params.fetch_method,
    language: params.language,
    country: params.country,
  } as const;
}

/**
 * Safely strip HTML tags and decode entities for display as plain text.
 * Uses DOMParser in the browser. Falls back to a basic regex strip if unavailable.
 */
export function stripHtml(html: string): string {
  if (!html) return '';
  try {
    if (typeof window !== 'undefined' && 'DOMParser' in window) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      return doc.body.textContent || '';
    }
  } catch (e) {
    // fall through to regex fallback
  }

  // Fallback: remove tags and decode common entities
  const tmp = html.replace(/<[^>]*>/g, '');
  return tmp.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
}