import { OpenAIService } from './openai';
import { StorageManager } from '../storage/storage';

export interface LLMRequest {
  systemPrompt: string;
  userPrompt: string;
  temperature?: number;
  maxTokens?: number;
}

export interface LLMResponse {
  content: string;
  success: boolean;
  error?: string;
}

export class LLMCaller {
  private static instance: LLMCaller;
  private storageManager: StorageManager;

  private constructor() {
    this.storageManager = StorageManager.getInstance();
  }

  public static getInstance(): LLMCaller {
    if (!LLMCaller.instance) {
      LLMCaller.instance = new LLMCaller();
    }
    return LLMCaller.instance;
  }

  async callLLM(request: LLMRequest): Promise<LLMResponse> {
    try {
      // Get AI configuration
      const settings = await this.storageManager.getSettings();
      const aiConfig = settings.aiConfiguration;

      // Create OpenAI service instance
      const openAIService = OpenAIService.getInstance({
        apiKey: aiConfig.openaiApiKey,
        model: aiConfig.openaiModel
      });

      // Make completion request
      const response = await openAIService.completion({
        systemPrompt: request.systemPrompt,
        prompt: request.userPrompt,
        temperature: request.temperature || 0.7,
        maxTokens: request.maxTokens || 500
      });

      return {
        content: response.content,
        success: true
      };

    } catch (error) {
      console.error('LLM call failed:', error);
      return {
        content: '',
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
}