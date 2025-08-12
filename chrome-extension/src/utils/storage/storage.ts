import { AppSettings, DEFAULT_PERSONAL_PREFERENCES, DEFAULT_AI_CONFIGURATION } from './types';

const STORAGE_KEY = 'nightcrawler-settings';

export class StorageManager {
  private static instance: StorageManager;

  private constructor() {}

  public static getInstance(): StorageManager {
    if (!StorageManager.instance) {
      StorageManager.instance = new StorageManager();
    }
    return StorageManager.instance;
  }

  async getSettings(): Promise<AppSettings> {
    return new Promise((resolve) => {
      (chrome as any).storage.local.get([STORAGE_KEY], (result: any) => {
        const settings = result[STORAGE_KEY] || {};
        resolve({
          personalPreferences: { ...DEFAULT_PERSONAL_PREFERENCES, ...settings.personalPreferences },
          aiConfiguration: { ...DEFAULT_AI_CONFIGURATION, ...settings.aiConfiguration }
        });
      });
    });
  }

  async saveSettings(settings: AppSettings): Promise<void> {
    return new Promise((resolve) => {
      (chrome as any).storage.local.set({ [STORAGE_KEY]: settings }, () => {
        resolve();
      });
    });
  }

  async updatePersonalPreferences(preferences: { [key: string]: string }): Promise<void> {
    const settings = await this.getSettings();
    settings.personalPreferences = preferences;
    await this.saveSettings(settings);
  }

  async updateAIConfiguration(aiConfig: { openaiApiKey: string; openaiModel: 'gpt-4o' }): Promise<void> {
    const settings = await this.getSettings();
    settings.aiConfiguration = aiConfig;
    await this.saveSettings(settings);
  }
}