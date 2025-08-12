// Base AI service interface
export interface AIServiceConfig {
  apiKey: string;
  model: string;
}

export interface CompletionRequest {
  prompt: string;
  systemPrompt?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface CompletionResponse {
  content: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

export abstract class AIService {
  protected config: AIServiceConfig;

  constructor(config: AIServiceConfig) {
    this.config = config;
  }

  abstract validateConfig(): boolean;
  abstract completion(request: CompletionRequest): Promise<CompletionResponse>;
  
  // Future: streaming completions
  // abstract streamCompletion(request: CompletionRequest): AsyncGenerator<string>;
}