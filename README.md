# 🕷️ Nightcrawler

> **⚠️ Work in Progress - Not Production Ready**  
> This Chrome extension is currently under active development and should not be used in production environments.

An AI-powered Chrome extension that analyzes LinkedIn job postings for personal fit assessment. Nightcrawler crawls job descriptions and company information, then uses AI to provide instant feedback on whether a position matches your preferences and profile.

## 🎯 What It Does

Nightcrawler integrates seamlessly with LinkedIn's job pages to:

- **Extract job information** from LinkedIn job postings (description, company details)
- **Analyze job fit** using AI based on your personal preferences and profile
- **Provide instant feedback** with a simple "Good fit" or "Not a good fit" assessment
- **Manage preferences** through a comprehensive settings interface

## 🏗️ Main Components

### Content Injection (`src/matcher.tsx`)
- Detects LinkedIn job pages and injects the match analysis button
- Extracts job descriptions from `.job-details-module` 
- Extracts company information from `.jobs-company`
- Handles DOM traversal and anti-scraping measures

### Match Button (`src/components/match-button/`)
- React component that appears next to LinkedIn's save button
- Styled with inline CSS to avoid conflicts with LinkedIn's styling
- Triggers job analysis when clicked

### AI Analysis System (`src/utils/ai/`)
- **Job Matcher** (`components/job-matcher.ts`): Core analysis logic
- **Prompts** (`prompts/job-matcher.ts`): AI prompts for job fit assessment
- **LLM Caller** (`llm-caller.ts`): OpenAI API integration
- **Preference Optimizers** (`components/preference-optimizer.ts`): Individual preference optimization

### Settings Interface (`src/components/settings/`)
- React-based settings page for managing preferences
- AI configuration (OpenAI API key, model selection)
- Personal preferences management (job title, experience, technologies, etc.)
- Individual "Optimize" buttons for each preference using AI

### Storage Management (`src/utils/storage/`)
- Chrome extension storage wrapper
- Settings persistence and retrieval
- Type-safe storage operations

## 🛠️ Technical Stack

- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS + Inline CSS (for LinkedIn compatibility)
- **Build System**: Webpack 5 with dynamic entry discovery
- **AI Integration**: OpenAI GPT models via REST API
- **Extension**: Chrome Manifest V3

## 📁 Project Structure

```
src/
├── matcher.tsx                 # Main content script
├── background.tsx              # Service worker
├── components/
│   ├── match-button/           # LinkedIn integration button
│   └── settings/               # Settings interface
├── utils/
│   ├── ai/                     # AI analysis system
│   │   ├── components/         # AI service components
│   │   ├── prompts/           # AI prompts
│   │   └── llm-caller.ts      # OpenAI integration
│   └── storage/               # Chrome storage management
└── styles/                    # Tailwind CSS styles
```

## 🚀 Development Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Build the extension**
   ```bash
   npm run build
   ```

3. **Load in Chrome**
   - Open Chrome Extensions (`chrome://extensions/`)
   - Enable Developer mode
   - Click "Load unpacked" and select the `dist` folder

4. **Configure API**
   - Set up OpenAI API key in extension settings
   - Configure personal preferences

## ⚡ Key Features

- **Smart Extraction**: Bypasses LinkedIn's anti-scraping measures by finding visible content
- **AI-Powered Analysis**: Uses OpenAI to analyze job fit in 2 lines maximum
- **Preference Management**: Comprehensive system for managing career preferences
- **Real-time Integration**: Seamlessly integrates with LinkedIn's UI
- **Type Safety**: Full TypeScript implementation with proper typing

## 🔧 Build System

- **Dynamic Entry Discovery**: Automatically finds all TSX files for webpack entry points
- **Automatic Asset Management**: Handles icons, styles, and manifest copying
- **No Code Splitting**: Optimized for Chrome extension environment
- **Development-friendly**: Hot reload and source maps in development mode

## 📝 Current Status

This extension is under active development. Current functionality includes:

- ✅ LinkedIn job page detection
- ✅ Job description and company extraction  
- ✅ AI-powered job matching analysis
- ✅ Settings interface with preference management
- ✅ Chrome extension infrastructure

## 🤝 Contributing

This is currently a work-in-progress project. Contributions, suggestions, and feedback are welcome as development continues.

---

**Note**: This extension requires an OpenAI API key to function. Make sure to configure your API credentials in the settings before use.