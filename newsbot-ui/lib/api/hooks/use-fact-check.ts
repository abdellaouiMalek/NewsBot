"use client";

import { useMutation } from "@tanstack/react-query";
import { FactCheckRequest } from "../schemas/fact-check.schema";
import { factCheckService } from "../services/fact-check.service";

/**
 * Hook to perform fact-checking on an article
 */
export function useFactCheck() {
  return useMutation({
    mutationFn: (request: FactCheckRequest) =>
      factCheckService.factCheck(request),
  });
}
