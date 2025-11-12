'use client';

import { useMutation, useQuery, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { articleService } from '../services/article.service';
import { Article, ArticleQueryParams } from '../schemas/article.schema';

/**
 * Query keys for article-related queries
 */
export const articleKeys = {
  all: ['articles'] as const,
  lists: () => [...articleKeys.all, 'list'] as const,
  list: (params?: Partial<ArticleQueryParams>) => [...articleKeys.lists(), params] as const,
  details: () => [...articleKeys.all, 'detail'] as const,
  detail: (id: string) => [...articleKeys.details(), id] as const,
  search: (query: string, params?: Partial<ArticleQueryParams>) => 
    [...articleKeys.all, 'search', query, params] as const,
  categories: () => [...articleKeys.all, 'categories'] as const,
};

/**
 * Hook to get articles list
 */
export function useArticles(params?: Partial<ArticleQueryParams>) {
  return useQuery({
    queryKey: articleKeys.list(params),
    queryFn: () => articleService.getArticles(params),
  });
}

/**
 * Hook to get single article
 */
export function useArticle(id: string) {
  return useQuery({
    queryKey: articleKeys.detail(id),
    queryFn: () => articleService.getArticleById(id),
    enabled: !!id,
  });
}

/**
 * Hook for infinite scroll articles
 */
export function useInfiniteArticles(params?: Partial<ArticleQueryParams>) {
  return useInfiniteQuery({
    queryKey: articleKeys.list(params),
    queryFn: ({ pageParam = 1 }) => 
      articleService.getArticles({ ...params, page: pageParam }),
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.total_pages) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    initialPageParam: 1,
  });
}

/**
 * Hook to create article
 */
export function useCreateArticle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<Article, 'id' | 'created_at' | 'updated_at'>) => 
      articleService.createArticle(data),
    onSuccess: () => {
      // Invalidate articles list
      queryClient.invalidateQueries({ queryKey: articleKeys.lists() });
    },
  });
}

/**
 * Hook to update article
 */
export function useUpdateArticle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Article> }) =>
      articleService.updateArticle(id, data),
    onSuccess: (data) => {
      // Invalidate specific article and list
      queryClient.invalidateQueries({ queryKey: articleKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: articleKeys.lists() });
    },
  });
}

/**
 * Hook to delete article
 */
export function useDeleteArticle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => articleService.deleteArticle(id),
    onSuccess: (_, id) => {
      // Remove from cache and invalidate list
      queryClient.removeQueries({ queryKey: articleKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: articleKeys.lists() });
    },
  });
}

/**
 * Hook to search articles
 */
export function useSearchArticles(query: string, params?: Partial<ArticleQueryParams>) {
  return useQuery({
    queryKey: articleKeys.search(query, params),
    queryFn: () => articleService.searchArticles(query, params),
    enabled: query.length > 0,
  });
}

/**
 * Hook to fetch available article categories
 */
export function useCategories() {
  return useQuery({
    queryKey: articleKeys.categories(),
    queryFn: () => articleService.getCategories(),
  });
}
