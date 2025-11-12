'use client';

import { useMutation } from '@tanstack/react-query';
import { chatService } from '../services/chat.service';
import { GenerateQueryRequest } from '../schemas/chat.schema';

/**
 * Hook to generate AI response from query
 */
export function useGenerateResponse() {
  return useMutation({
    mutationFn: (request: GenerateQueryRequest) => chatService.generate(request),
  });
}
