import axiosInstance from '../axios-instance';
import {
  Article,
  ArticleSchema,
  ArticleListResponse,
  ArticleListResponseSchema,
  ArticleQueryParams,
  ArticleQueryParamsSchema,
  ArticleCategoriesSchema,
} from '../schemas/article.schema';

/**
 * Articles API service
 */
export const articleService = {
  /**
   * Get list of articles with optional filters
   */
  getArticles: async (params?: Partial<ArticleQueryParams>): Promise<ArticleListResponse> => {
    const normalized: ArticleQueryParams = {
      page: params?.page ?? 1,
      page_size: params?.page_size ?? 20,
      category: params?.category,
      source_name: params?.source_name,
      fetch_method: params?.fetch_method,
      language: params?.language,
      country: params?.country,
    };

  const apiParams = ArticleQueryParamsSchema.parse(normalized);
  const response = await axiosInstance.get('/articles', { params: apiParams });
      // Backend now returns a paginated ArticleListResponse by default.
      // Try a safe parse first so we can log structured errors when the shape
      // doesn't match exactly (helps debugging during schema drift).
      const safe = ArticleListResponseSchema.safeParse(response.data);
      if (safe.success) return safe.data;

      // If parsing fails, log the error and attempt a best-effort fallback so the
      // UI can still render available articles instead of showing an error.
      console.error('[API] ArticleListResponse schema mismatch:', safe.error, 'response=', response.data);

      const data = response.data as any;
      // If the backend returned an object with articles array, try to use it.
      if (data && Array.isArray(data.articles)) {
        const fallback = {
          articles: data.articles,
          total: typeof data.total === 'number' ? data.total : data.articles.length,
          page: typeof data.page === 'number' ? data.page : normalized.page,
          page_size: typeof data.page_size === 'number' ? data.page_size : data.articles.length,
          total_pages: typeof data.total_pages === 'number' ? data.total_pages : 1,
        };
        return fallback as ArticleListResponse;
      }

      // As a last resort, if the response itself is an array of articles, wrap it.
      if (Array.isArray(data)) {
        const wrapped = {
          articles: data,
          total: data.length,
          page: normalized.page ?? 1,
          page_size: data.length,
          total_pages: 1,
        };
        return wrapped as unknown as ArticleListResponse;
      }

      // Nothing usable found - return an empty paginated response to avoid UI crash.
      return {
        articles: [],
        total: 0,
        page: normalized.page ?? 1,
        page_size: normalized.page_size ?? 10,
        total_pages: 0,
      } as ArticleListResponse;
  },

  /**
   * Get single article by ID
   */
  getArticleById: async (id: string): Promise<Article> => {
    const response = await axiosInstance.get(`/articles/${id}`);
    return ArticleSchema.parse(response.data);
  },

  /**
   * Create new article
   */
  createArticle: async (data: Omit<Article, 'id' | 'created_at' | 'updated_at'>): Promise<Article> => {
    const response = await axiosInstance.post('/articles', data);
    return ArticleSchema.parse(response.data);
  },

  /**
   * Update article
   */
  updateArticle: async (id: string, data: Partial<Article>): Promise<Article> => {
    const response = await axiosInstance.patch(`/articles/${id}`, data);
    return ArticleSchema.parse(response.data);
  },

  /**
   * Delete article
   */
  deleteArticle: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/articles/${id}`);
  },

  /**
   * Search articles
   */
  searchArticles: async (query: string, params?: Partial<ArticleQueryParams>): Promise<ArticleListResponse> => {
    const response = await axiosInstance.get('/articles/search', {
      params: { ...params, q: query },
    });
    return ArticleListResponseSchema.parse(response.data);
  },

  /**
   * Get available article categories
   */
  getCategories: async (): Promise<string[]> => {
    const response = await axiosInstance.get('/articles/categories');
    const remote = ArticleCategoriesSchema.parse(response.data);
    return ['All', ...remote];
  },
};
