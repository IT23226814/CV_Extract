# CV Analysis and Matching System

A Python-based application that analyzes CVs and matches them against job requirements using AI-powered text processing.

## Features

- Upload and process PDF CVs
- Automatically extract candidate information using GenAI
- Create and manage job templates
- Match candidates to job requirements with detailed scoring
- Database storage for candidates and job templates
- Interactive web interface using Streamlit

## Prerequisites

- Python 3.11
- Required API keys:
  - Google AI API key (for Gemini model)
  - Groq API key (for Deepseek R1)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Set up environment variables:
```bash
export GOOGLE_API_KEY="your-google-api-key"
export GROQ_API_KEY="your-groq-api-key"
```

3. Install dependencies:
```bash
pip install streamlit pdfminer.six google-generativeai groq pandas sqlite3
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Navigate to the web interface and use the sidebar to access different features:
   - Upload CV: Submit and process new CVs
   - Manage CVs: View, edit, or delete existing candidates
   - Create Job Template: Define new job requirements
   - Manage Job Templates: Edit or delete job templates
   - Match CVs: Compare candidates against job requirements

## Architecture

- `app.py`: Main Streamlit application and UI logic
- `cv_processor.py`: CV text extraction and AI-powered analysis
- `database.py`: SQLite database management
- Uses Google's Gemini model and Groq's LLM for AI processing

