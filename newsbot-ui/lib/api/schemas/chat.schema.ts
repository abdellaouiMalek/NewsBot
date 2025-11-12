import { z } from "zod";
import { ArticleSchema } from "./article.schema";

/**
 * Chat message schema
 */
export const ChatMessageSchema = z.object({
  id: z.string(),
  type: z.enum(["user", "agent"]),
  content: z.string(),
  timestamp: z.string().datetime(),
  action: z
    .object({
      type: z.enum(["filter", "sort", "search", "category"]),
      value: z.string(),
    })
    .optional(),
});

export type ChatMessage = z.infer<typeof ChatMessageSchema>;

/**
 * Generate query request schema
 */
export const GenerateQueryRequestSchema = z.object({
  query: z.string().min(1, "Query cannot be empty"),
  k: z.number().min(1).max(20).default(5),
});

export type GenerateQueryRequest = z.infer<typeof GenerateQueryRequestSchema>;

/**
 * Source document schema
 * The API returns sources as either strings or objects
 */
export const SourceDocumentSchema = z.union([
  z.string(),
  z.object({
    id: z.string().optional(),
    title: z.string().optional(),
    content: z.string(),
    url: z.string().url().optional(),
    source: z.string().optional(),
    score: z.number().optional(),
    metadata: z.record(z.any()).optional(),
  }),
]);

export type SourceDocument = z.infer<typeof SourceDocumentSchema>;

/**
 * Generate response schema
 */
export const GenerateResponseSchema = z.object({
  query: z.string(),
  context: z.string(),
  answer: z.string(),
  sources: z.array(z.string()).default([]), // Array of article IDs
  articles: z.array(ArticleSchema).default([]), // Full article objects
});

export type GenerateResponse = z.infer<typeof GenerateResponseSchema>;
