import { z } from 'zod';

/**
 * Article schema (aligned with backend Pydantic models)
 * Note: embedding fields are intentionally excluded per request.
 */
export const ArticleSchema = z.object({
  id: z.string(),
  article_id: z.string(),
  title: z.string(),
  content: z.string().optional(),
  summary: z.string().optional(),
  // author may be null in some backend responses
  author: z.string().optional().nullable(),
  // published_at / fetched_at may sometimes come as null or non-ISO values
  // (e.g. timestamps or loosely formatted strings). Coerce to string when
  // possible and accept null/undefined to avoid runtime parse failures.
  published_at: z.preprocess((val) => (val === null || val === undefined ? null : String(val)), z.string().optional().nullable()),
  fetched_at: z.preprocess((val) => (val === null || val === undefined ? null : String(val)), z.string().optional().nullable()),
  source_name: z.string(),
  source_url: z.string().url(),
  article_url: z.string().url(),
  category: z.string().optional(),
  language: z.string().optional(),
  country: z.string().optional().nullable(),
  fetch_method: z.string().optional(),
  media_thumbnail: z.string().optional().nullable(),
  tags: z.array(z.string()).default([]),
  sentiment: z.string().optional().nullable(),
  entities: z.string().optional().nullable(),
  raw_data: z.record(z.any()).optional(),
  // created_at / updated_at sometimes come as non-ISO strings or timestamps.
  // Coerce to string when present and allow null to avoid rejecting the whole
  // response during schema validation.
  created_at: z.preprocess((val) => (val === null || val === undefined ? null : String(val)), z.string().optional().nullable()),
  updated_at: z.preprocess((val) => (val === null || val === undefined ? null : String(val)), z.string().optional().nullable()),
});

export type Article = z.infer<typeof ArticleSchema>;

/**
 * Article list response schema
 */
export const ArticleListResponseSchema = z.object({
  articles: z.array(ArticleSchema),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
  total_pages: z.number(),
});

export type ArticleListResponse = z.infer<typeof ArticleListResponseSchema>;

/**
 * Article query params
 */
export const ArticleQueryParamsSchema = z.object({
  page: z.number().min(1).default(1),
  page_size: z.number().min(1).max(100).default(10),
  category: z.string().optional(),
  source_name: z.string().optional(),
  fetch_method: z.string().optional(),
  language: z.string().optional(),
  country: z.string().optional(),
});

export type ArticleQueryParams = z.infer<typeof ArticleQueryParamsSchema>;

/**
 * Categories response schema - simple array of strings
 */
export const ArticleCategoriesSchema = z.array(z.string());
export type ArticleCategories = z.infer<typeof ArticleCategoriesSchema>;
