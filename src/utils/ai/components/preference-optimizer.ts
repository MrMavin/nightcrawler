import { LLMCaller, LLMRequest } from '../llm-caller';
import { getOptimizerForKey } from '../prompts/optimizers';

export interface OptimizationResult {
  success: boolean;
  optimizedValue: string;
  error?: string;
}

export class PreferenceOptimizer {
  private static instance: PreferenceOptimizer;
  private llmCaller: LLMCaller;

  private constructor() {
    this.llmCaller = LLMCaller.getInstance();
  }

  public static getInstance(): PreferenceOptimizer {
    if (!PreferenceOptimizer.instance) {
      PreferenceOptimizer.instance = new PreferenceOptimizer();
    }
    return PreferenceOptimizer.instance;
  }

  async optimize(key: string, value: string): Promise<OptimizationResult> {
    try {
      // Get optimizer prompt based on key
      const optimizer = getOptimizerForKey(key);
      
      if (!optimizer) {
        return {
          success: false,
          optimizedValue: value, // Return original if no optimizer
          error: `No optimizer prompt found for key: ${key}`
        };
      }

      if (!value.trim()) {
        return {
          success: false,
          optimizedValue: value,
          error: 'No content to optimize'
        };
      }

      // Prepare LLM request
      const llmRequest: LLMRequest = {
        systemPrompt: optimizer.prompt,
        userPrompt: `Please optimize this ${key.toLowerCase()}: "${value}"`,
        temperature: 0.7,
        maxTokens: 500
      };

      // Call LLM
      const llmResponse = await this.llmCaller.callLLM(llmRequest);

      if (!llmResponse.success) {
        return {
          success: false,
          optimizedValue: value, // Return original on failure
          error: llmResponse.error || 'LLM call failed'
        };
      }

      return {
        success: true,
        optimizedValue: llmResponse.content
      };

    } catch (error) {
      console.error(`Optimization failed for ${key}:`, error);
      return {
        success: false,
        optimizedValue: value, // Return original on error
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
}