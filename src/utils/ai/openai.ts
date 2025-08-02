import { AIService, AIServiceConfig, CompletionRequest, CompletionResponse } from './base';

export class OpenAIService extends AIService {
  private static instance: OpenAIService | null = null;

  constructor(config: AIServiceConfig) {
    super(config);
  }

  static getInstance(config: AIServiceConfig): OpenAIService {
    if (!OpenAIService.instance || !OpenAIService.instance.validateConfig()) {
      OpenAIService.instance = new OpenAIService(config);
    }
    return OpenAIService.instance;
  }

  validateConfig(): boolean {
    return !!(this.config.apiKey && this.config.apiKey.startsWith('sk-'));
  }

  async completion(request: CompletionRequest): Promise<CompletionResponse> {
    if (!this.validateConfig()) {
      throw new Error('Invalid OpenAI configuration. Please check your API key.');
    }

    const messages = [];
    
    if (request.systemPrompt) {
      messages.push({ role: 'system', content: request.systemPrompt });
    }
    
    messages.push({ role: 'user', content: request.prompt });

    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({
          model: this.config.model,
          messages,
          temperature: request.temperature || 0.7,
          max_tokens: request.maxTokens || 500
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error?.message || `OpenAI API error: ${response.status}`);
      }

      const content = data.choices[0].message.content.trim();
      
      return {
        content: content.replace(/^["']|["']$/g, ''), // Remove wrapping quotes
        usage: data.usage ? {
          promptTokens: data.usage.prompt_tokens,
          completionTokens: data.usage.completion_tokens,
          totalTokens: data.usage.total_tokens
        } : undefined
      };
      
    } catch (error) {
      console.error('OpenAI completion error:', error);
      throw error;
    }
  }
}