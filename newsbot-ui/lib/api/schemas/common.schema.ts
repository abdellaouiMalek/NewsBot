import { z } from 'zod';

/**
 * Common API response wrapper
 */
export const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema,
    message: z.string().optional(),
    timestamp: z.string().datetime().optional(),
  });

/**
 * API Error response
 */
export const ApiErrorSchema = z.object({
  success: z.literal(false),
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.any().optional(),
  }),
  timestamp: z.string().datetime().optional(),
});

export type ApiError = z.infer<typeof ApiErrorSchema>;

/**
 * Pagination metadata
 */
export const PaginationMetaSchema = z.object({
  page: z.number(),
  page_size: z.number(),
  total: z.number(),
  total_pages: z.number(),
});

export type PaginationMeta = z.infer<typeof PaginationMetaSchema>;
