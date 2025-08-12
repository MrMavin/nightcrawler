import { createJobMatchPrompt } from '../prompts/job-matcher';
import { LLMCaller } from '../llm-caller';

export interface JobMatchRequest {
  jobDescription: string;
  companyInfo: string;
  userPreferences: string;
}

export interface JobMatchResult {
  success: boolean;
  analysis: string;
  error?: string;
}

/**
 * Analyzes job fit based on job description, company info, and user preferences
 * Returns a 2-line analysis indicating if it's a good fit
 */
export async function analyzeJobMatch(request: JobMatchRequest): Promise<JobMatchResult> {
  try {
    const { jobDescription, companyInfo, userPreferences } = request;
    
    if (!jobDescription.trim()) {
      return {
        success: false,
        analysis: '',
        error: 'Job description is required for analysis'
      };
    }

    const prompt = createJobMatchPrompt(jobDescription, companyInfo, userPreferences);
    const llmCaller = LLMCaller.getInstance();
    
    const response = await llmCaller.callLLM({
      systemPrompt: 'You are an expert career advisor specializing in job fit analysis.',
      userPrompt: prompt,
      maxTokens: 512, // Keep it concise - 2 lines max
      temperature: 0.5
    });

    if (response.success) {
      return {
        success: true,
        analysis: response.content.trim()
      };
    } else {
      return {
        success: false,
        analysis: '',
        error: response.error || 'AI analysis failed'
      };
    }

  } catch (error) {
    console.error('Job match analysis failed:', error);
    return {
      success: false,
      analysis: '',
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}