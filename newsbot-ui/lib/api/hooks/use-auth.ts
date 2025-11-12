'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService } from '../services/auth.service';
import { LoginRequest, SignupRequest } from '../schemas/auth.schema';

/**
 * Query keys for auth-related queries
 */
export const authKeys = {
  all: ['auth'] as const,
  currentUser: () => [...authKeys.all, 'current-user'] as const,
};

/**
 * Hook to get current user
 */
export function useCurrentUser() {
  return useQuery({
    queryKey: authKeys.currentUser(),
    queryFn: authService.getCurrentUser,
    // Don't retry on 401
    retry: (failureCount, error: any) => {
      if (error?.response?.status === 401) return false;
      return failureCount < 3;
    },
  });
}

/**
 * Hook to login
 */
export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: LoginRequest) => authService.login(credentials),
    onSuccess: (data) => {
      // Store token
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', data.token);
      }
      // Invalidate current user query to refetch
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
}

/**
 * Hook to signup
 */
export function useSignup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SignupRequest) => authService.signup(data),
    onSuccess: (data) => {
      // Store token
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', data.token);
      }
      // Invalidate current user query to refetch
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
}

/**
 * Hook to logout
 */
export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      // Clear all queries
      queryClient.clear();
    },
  });
}
