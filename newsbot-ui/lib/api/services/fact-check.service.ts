import axiosInstance from "../axios-instance";
import {
  FactCheckRequest,
  FactCheckResponse,
  FactCheckResponseSchema,
} from "../schemas/fact-check.schema";

/**
 * Fact Check Service
 * Handles all fact-checking related API calls
 */
export const factCheckService = {
  /**
   * Perform fact-checking on an article
   * Uses LLM to search for similar articles from different sources
   * and perform comparative analysis
   *
   * Note: This endpoint has an extended timeout (300s) because:
   * - Semantic search for similar articles across sources
   * - Multiple LLM calls for each source comparison (can be 5-6 calls)
   * - Overall assessment generation
   * - Each LLM call can take 20-30 seconds
   */
  async factCheck(request: FactCheckRequest): Promise<FactCheckResponse> {
    const response = await axiosInstance.post("/fact-check/", request, {
      timeout: 300000, // 300 seconds (5 minutes) for comprehensive fact-checking
    });
    return FactCheckResponseSchema.parse(response.data);
  },
};
