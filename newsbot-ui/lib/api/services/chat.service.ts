import axiosInstance from '../axios-instance';
import {
  GenerateQueryRequest,
  GenerateResponse,
  GenerateResponseSchema,
} from '../schemas/chat.schema';

/**
 * Chat API service
 */
export const chatService = {
  /**
   * Generate AI response based on query
   * Uses RAG pipeline to search articles and generate answer
   * 
   * Note: This endpoint has an extended timeout (120s) because:
   * - RAG retrieval can take time with large vector databases
   * - LLM inference can be slow depending on model and hardware
   * - Context processing and embedding generation add overhead
   */
  generate: async (request: GenerateQueryRequest): Promise<GenerateResponse> => {
    const response = await axiosInstance.post('/generate', request, {
      timeout: 120000, // 120 seconds for RAG/LLM operations
    });
    return GenerateResponseSchema.parse(response.data);
  },
};
