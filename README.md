# Kutbi

Kutbi is an AI-powered tool that transforms YouTube technical videos into structured, actionable Notion Application Guides.

## Features
- **YouTube Integration:** Seamlessly fetch channel uploads or process specific videos.
- **Smart Transcription:** Leverages `yt-dlp` and `youtube-transcript-api` to generate high-quality transcripts.
- **AI-Powered Synthesis:** Uses advanced LLMs (via OpenRouter or Gemini) to create comprehensive guides, including big ideas, tools used, implementation steps, and code snippets.
- **Notion Integration:** Automatically organizes guides into a structured Notion database for easy reference and action.

## Getting Started

### Prerequisites
- Python 3.10+
- An API key for Notion, and either OpenRouter or Gemini.

### Installation
1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
4. Install dependencies: `pip install -r requirements.txt`

### Configuration
Create a `.env` file in the root directory:
```env
OPENROUTER_API_KEY=your_openrouter_key
NOTION_API_KEY=your_notion_key
GEMINI_API_KEY=your_gemini_key
```

### Running Kutbi
1. Start the backend: `python -m backend.main`
2. Start the frontend: `streamlit run frontend/app.py`
"""
