# API Architecture Documentation

## 📁 Folder Structure

```
lib/api/
├── axios-instance.ts       # Global axios instance with interceptors
├── index.ts               # Main exports
├── hooks/                 # React Query hooks
│   ├── use-auth.ts       # Authentication hooks
│   └── use-articles.ts   # Article management hooks
├── schemas/              # Zod schemas for validation
│   ├── auth.schema.ts   # Auth-related schemas
│   ├── article.schema.ts # Article-related schemas
│   └── common.schema.ts  # Shared schemas
└── services/            # API service functions
    ├── auth.service.ts  # Auth API calls
    └── article.service.ts # Article API calls
```

## 🚀 Quick Start

### 1. Environment Variables

Add to your `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 2. Using API Hooks

```tsx
import { useArticles, useArticle, useCreateArticle } from '@/lib/api';

function ArticlesList() {
  // Get articles with filters
  const { data, isLoading, error } = useArticles({
    page: 1,
    page_size: 20,
    category: 'technology',
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data?.articles.map(article => (
        <ArticleCard key={article.id} article={article} />
      ))}
    </div>
  );
}
```

### 3. Mutations (Create, Update, Delete)

```tsx
import { useCreateArticle, useUpdateArticle, useDeleteArticle } from '@/lib/api';

function ArticleActions() {
  const createMutation = useCreateArticle();
  const updateMutation = useUpdateArticle();
  const deleteMutation = useDeleteArticle();

  const handleCreate = async () => {
    try {
      await createMutation.mutateAsync({
        title: 'New Article',
        content: 'Article content...',
        url: 'https://example.com',
        source: 'Example Source',
        published_at: new Date().toISOString(),
      });
      // Success - queries will auto-refresh
    } catch (error) {
      console.error('Failed to create:', error);
    }
  };

  const handleUpdate = async (id: string) => {
    await updateMutation.mutateAsync({
      id,
      data: { title: 'Updated Title' },
    });
  };

  const handleDelete = async (id: string) => {
    await deleteMutation.mutateAsync(id);
  };

  return <div>...</div>;
}
```

### 4. Authentication

```tsx
import { useLogin, useSignup, useLogout, useCurrentUser } from '@/lib/api';

function AuthComponent() {
  const login = useLogin();
  const signup = useSignup();
  const logout = useLogout();
  const { data: user, isLoading } = useCurrentUser();

  const handleLogin = async () => {
    try {
      await login.mutateAsync({
        email: 'user@example.com',
        password: 'password123',
      });
      // Token is automatically stored and user is fetched
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return <div>...</div>;
}
```

### 5. Infinite Scroll

```tsx
import { useInfiniteArticles } from '@/lib/api';

function InfiniteArticlesList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteArticles({ page_size: 20 });

  return (
    <div>
      {data?.pages.map((page) =>
        page.articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))
      )}
      
      {hasNextPage && (
        <button
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
        >
          {isFetchingNextPage ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}
```

## 🔧 Creating New Services

### 1. Define Schema (schemas/feature.schema.ts)

```tsx
import { z } from 'zod';

export const FeatureSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  // ... other fields
});

export type Feature = z.infer<typeof FeatureSchema>;
```

### 2. Create Service (services/feature.service.ts)

```tsx
import axiosInstance from '../axios-instance';
import { Feature, FeatureSchema } from '../schemas/feature.schema';

export const featureService = {
  getAll: async (): Promise<Feature[]> => {
    const response = await axiosInstance.get('/features');
    return z.array(FeatureSchema).parse(response.data);
  },
  
  getById: async (id: string): Promise<Feature> => {
    const response = await axiosInstance.get(`/features/${id}`);
    return FeatureSchema.parse(response.data);
  },
  
  create: async (data: Omit<Feature, 'id'>): Promise<Feature> => {
    const response = await axiosInstance.post('/features', data);
    return FeatureSchema.parse(response.data);
  },
};
```

### 3. Create Hooks (hooks/use-feature.ts)

```tsx
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { featureService } from '../services/feature.service';

export const featureKeys = {
  all: ['features'] as const,
  lists: () => [...featureKeys.all, 'list'] as const,
  detail: (id: string) => [...featureKeys.all, 'detail', id] as const,
};

export function useFeatures() {
  return useQuery({
    queryKey: featureKeys.lists(),
    queryFn: featureService.getAll,
  });
}

export function useFeature(id: string) {
  return useQuery({
    queryKey: featureKeys.detail(id),
    queryFn: () => featureService.getById(id),
    enabled: !!id,
  });
}

export function useCreateFeature() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: featureService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: featureKeys.lists() });
    },
  });
}
```

### 4. Export in index.ts

```tsx
export * from './services/feature.service';
export * from './schemas/feature.schema';
export * from './hooks/use-feature';
```

## 🎯 Best Practices

1. **Always use schemas** - Validate all API responses with Zod schemas
2. **Use query keys consistently** - Follow the pattern: `['resource', 'action', ...params]`
3. **Handle loading and error states** - Always check `isLoading` and `error`
4. **Invalidate queries after mutations** - Ensure UI stays in sync
5. **Use optimistic updates** - For better UX on mutations
6. **Enable queries conditionally** - Use `enabled` option when appropriate

## 📊 TanStack Query DevTools

In development mode, DevTools are automatically enabled. Access them via the floating icon in your app.

## 🔐 Authentication Flow

1. User logs in via `useLogin()`
2. Token is stored in localStorage
3. Axios interceptor adds token to all requests
4. `useCurrentUser()` fetches user data
5. On 401 error, user is redirected to login

## 🎨 TypeScript Benefits

- Full type safety across API calls
- IntelliSense support
- Compile-time error checking
- Auto-completion for API parameters
