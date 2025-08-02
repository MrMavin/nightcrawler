import React from 'react';
import { createRoot, Root } from 'react-dom/client';
import MatchButton from './components/match-button/match-button';
import { StorageManager } from './utils/storage/storage';
import { analyzeJobMatch } from './utils/ai/components/job-matcher';

class ReactContentMatcher {
  private root: Root | null = null;
  private container: HTMLElement | null = null;

  private isJobPage(): boolean {
    const url = window.location.href;
    return url.includes("/jobs/");
  }

  private findJobDetailsContainer(): HTMLElement | null {
    const saveButton = this.findSaveButton();
    if (!saveButton) return null;
    
    // Traverse up from save button to find .jobs-details container
    let element = saveButton.parentElement;
    while (element && element !== document.body) {
      if (element.classList.contains('jobs-details')) {
        return element;
      }
      element = element.parentElement;
    }
    return null;
  }

  private extractJobDescription(): string {
    const jobDetails = this.findJobDetailsContainer();
    const jobDetailsModules = jobDetails?.querySelectorAll(".job-details-module");
    
    if (!jobDetailsModules) return "";
    
    // Iterate through all job-details-module elements to find one with actual content
    for (const module of Array.from(jobDetailsModules)) {
      const element = module as HTMLElement;
      
      // Skip if hidden
      if (element.style.display === 'none' || 
          element.hidden || 
          element.offsetHeight === 0 || 
          element.offsetWidth === 0) {
        continue;
      }
      
      // Check if it has meaningful content
      const content = element.innerText?.trim();
      if (content && content.length > 50) { // At least 50 characters for a real job description
        console.log('✅ Found visible job-details-module with content');
        return content;
      }
    }
    
    console.log('❌ No visible job-details-module found with content');
    return "";
  }

  private extractCompanyInfo(): string {
    const jobDetails = this.findJobDetailsContainer();
    const jobsCompanies = jobDetails?.querySelectorAll(".jobs-company");
    
    if (!jobsCompanies) return "";
    
    // Iterate through all jobs-company elements to find one with actual content
    for (const company of Array.from(jobsCompanies)) {
      const element = company as HTMLElement;
      
      // Skip if hidden
      if (element.style.display === 'none' || 
          element.hidden || 
          element.offsetHeight === 0 || 
          element.offsetWidth === 0) {
        continue;
      }
      
      // Check if it has meaningful content
      const content = element.innerText?.trim();
      if (content && content.length > 2) { // At least a few characters for company name
        console.log('✅ Found visible jobs-company with content');
        return content;
      }
    }
    
    console.log('❌ No visible jobs-company found with content');
    return "";
  }

  private async getUserPreferences(): Promise<string> {
    try {
      const storageManager = StorageManager.getInstance();
      const settings = await storageManager.getSettings();
      
      const preferences = settings.personalPreferences;
      const prefStrings = Object.entries(preferences)
        .filter(([, value]) => value && value.trim()) // Filter out empty values
        .map(([key, value]) => `${key}: ${value}`)
        .join('\n');
        
      return prefStrings || 'No preferences configured in settings';
    } catch (error) {
      console.error('Failed to get user preferences:', error);
      return 'Error loading preferences from settings';
    }
  }

  private async handleJobAnalysis(): Promise<void> {
    console.log('🎯 Starting job analysis...');
    
    const jobDescription = this.extractJobDescription();
    const companyInfo = this.extractCompanyInfo();
    
    console.log('📋 Job Description:', jobDescription.substring(0, 200) + '...');
    console.log('🏢 Company Info:', companyInfo.substring(0, 100) + '...');

    if (!jobDescription && !companyInfo) {
      alert('❌ Could not extract job information from this page.');
      return;
    }

    try {
      const userPreferences = await this.getUserPreferences();
      console.log('👤 User Preferences:', userPreferences);

      // Use the job matcher
      
      const result = await analyzeJobMatch({
        jobDescription,
        companyInfo,
        userPreferences
      });

      if (result.success) {
        alert(`🎯 Job Match Analysis\n\n${result.analysis}`);
      } else {
        alert(`❌ Analysis failed: ${result.error || 'Unknown error'}`);
      }

    } catch (error) {
      console.error('Job analysis error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`❌ Analysis failed: ${errorMessage}`);
    }
  }

  private getJobViewLayout(): HTMLElement | null {
    return document.querySelector(".job-view-layout.jobs-details");
  }

  private findSaveButton(): HTMLElement | null {
    const jobViewLayout = this.getJobViewLayout();
    console.log('🏗️ Job view layout:', jobViewLayout);
    
    const button = jobViewLayout?.querySelector(".jobs-save-button");
    console.log('🔍 Save button query result:', button);
    
    if (button) {
      return button as HTMLElement;
    }
    return null;
  }

  private createReactContainer(): HTMLElement {
    // Remove existing container if any
    const existing = document.getElementById('nightcrawler-content-app');
    if (existing) {
      existing.remove();
    }

    const container = document.createElement('div');
    container.id = 'nightcrawler-content-app';
    container.style.cssText = `
      display: inline-block;
      margin-left: 8px;
    `;
    
    return container;
  }

  public init(): void {
    console.log('🚀 Initializing React Content Matcher...');
    
    const isJobPage = this.isJobPage();
    console.log('📍 Is job page:', isJobPage);
    
    const saveButton = this.findSaveButton();
    console.log('💾 Save button found:', !!saveButton, saveButton);

    if (isJobPage && saveButton) {
      // Create React container next to save button
      this.container = this.createReactContainer();
      const flexContainer = saveButton.parentElement;
      console.log('📦 Parent container:', flexContainer);
      
      if (flexContainer) {
        flexContainer.appendChild(this.container);
        
        // Create React root and render app
        this.root = createRoot(this.container);
        this.root.render(
          <MatchButton 
            isJobPage={isJobPage} 
            saveButton={saveButton}
            onAnalyzeMatch={() => this.handleJobAnalysis()}
          />
        );
        
        console.log('✅ React Content App rendered');
      } else {
        console.log('❌ No parent container found for save button');
      }
    } else {
      console.log('❌ Conditions not met - isJobPage:', isJobPage, 'saveButton:', !!saveButton);
      // Clean up if not on job page
      this.cleanup();
    }
  }

  public cleanup(): void {
    if (this.root) {
      this.root.unmount();
      this.root = null;
    }
    if (this.container) {
      this.container.remove();
      this.container = null;
    }
  }
}

// Wait for DOM to be ready
function waitForDOMReady(): Promise<void> {
  return new Promise((resolve) => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => resolve());
    } else {
      resolve();
    }
  });
}

// Wait for network activity to settle (simple version)
function waitForNetworkIdle(timeout = 2000): Promise<void> {
  return new Promise((resolve) => {
    let timer: ReturnType<typeof setTimeout>;
    
    const resetTimer = () => {
      clearTimeout(timer);
      timer = setTimeout(() => resolve(), timeout);
    };
    
    // Listen for fetch requests (modern way)
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
      resetTimer();
      return originalFetch.apply(this, args);
    };
    
    // Start initial timer
    resetTimer();
  });
}

// Initialize the matcher with proper timing
async function initializeExtension() {
  console.log("🌟 Content script loaded!");
  
  // Wait for DOM to be ready
  await waitForDOMReady();
  console.log("📄 DOM ready");
  
  // Wait a bit more for LinkedIn's initial content to load
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Wait for network to be relatively idle
  await waitForNetworkIdle(1500);
  console.log("🌐 Network idle, initializing matcher...");
  
  const matcher = new ReactContentMatcher();
  matcher.init();
  
  // Re-initialize when navigating to new pages (LinkedIn is SPA)
  let currentUrl = window.location.href;
  setInterval(() => {
    if (window.location.href !== currentUrl) {
      console.log("🔄 URL changed, waiting before re-init...");
      currentUrl = window.location.href;
      setTimeout(async () => {
        console.log("⏰ Re-initializing after URL change...");
        // Wait for new page content to load
        await new Promise(resolve => setTimeout(resolve, 1000));
        await waitForNetworkIdle(1000);
        matcher.init();
      }, 1000);
    }
  }, 1000);
}

// Start the initialization process
initializeExtension();
