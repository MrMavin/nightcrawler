// Store type definitions
export interface PersonalPreference {
  key: string;
  value: string;
}

export interface PersonalPreferences {
  [key: string]: string;
}

export interface AIConfiguration {
  openaiApiKey: string;
  openaiModel: "gpt-4o";
}

export interface AppSettings {
  personalPreferences: PersonalPreferences;
  aiConfiguration: AIConfiguration;
}

// Default values
export const DEFAULT_PERSONAL_PREFERENCES: PersonalPreferences = {
  "Job Title": "",
  Experience: "",
  Technologies: "",
  "Technologies To Avoid": "",
  Education: "",
  "Work Style": "",
  Location: "",
  "Salary Expectations": "",
  Aspirations: "",
};

export const DEFAULT_AI_CONFIGURATION: AIConfiguration = {
  openaiApiKey: "",
  openaiModel: "gpt-4o",
};
