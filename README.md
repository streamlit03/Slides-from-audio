Here is the complete, professional README.md in English. It is designed to be highly readable, technical enough for developers, and clear enough for any user who finds your repository.

🪄 AI Transcription & Slide Creator
Turn your voice into professional, high-level corporate presentations in seconds. This application leverages state-of-the-art AI to transcribe audio, analyze strategic content, and automatically generate editable PowerPoint and PDF files. It doesn't just transcribe; it acts as a Strategic Consultant to structure your ideas into a professional narrative.

🌟 Key Features
🎙️ Dual Audio Input: Record directly via your browser or upload existing files (mp3, wav, m4a, etc.).

🌍 Intelligent Language Detection: The system automatically detects the audio language and adapts the entire output (including UI labels like "Speaker Notes") to match the detected language.

🧠 Hybrid AI Architecture: * Whisper (OpenAI): High-precision local transcription.

Gemini 2.5 Flash (Google): Advanced LLM for semantic analysis and executive prose generation.

📊 Automated Document Rendering: Generates structured slides (Title, Body, and Speaker Notes) without manual intervention.

🎨 Modern UI/UX: Styled with custom CSS, glassmorphism effects, and dynamic backgrounds for a premium experience.

🛠️ Technical Tech Stack
Framework: Streamlit

Transcription Engine: openai-whisper (Base model)

Generative Engine: google-generativeai (Gemini 2.5 Flash)

Document Processing:

python-pptx: For dynamic PowerPoint generation.

reportlab: For high-fidelity PDF canvas drawing.

Parsing: Regular Expressions (re) for structured data extraction.

🧠 Code Logic & Data Flow
This project follows a sophisticated data pipeline to ensure professional results:

Ingestion: Captures audio buffer, validating file size (up to 30MB).

Transcription & Meta-data: Whisper processes the audio, returning raw text and a detected_language_code (e.g., es, en, fr).

Dynamic Language Mapping: A translation dictionary (translations_map) uses the language code to localize labels in the final document, ensuring "Speaker Notes" appears in the correct language.

Strategic Prompting: Gemini is instructed to act as a Strategic Consultant. It is specifically forbidden from using bullet points, forced to use fluid prose, and tasked with creating exactly 5 slides even from short inputs.

Structural Parsing: Using Regex, the script isolates Slide Titles, Body Content, and Speaker Notes marked by ###NOTAS###.

Rendering: The content is injected into a template.pptx base, programmatically adjusting font sizes (Pt) and layouts to prevent text overflow.

🚀 Local Setup
1. Prerequisites
You must have FFmpeg installed on your system for Whisper to handle audio processing.

Windows: choco install ffmpeg

MacOS: brew install ffmpeg

Linux: sudo apt install ffmpeg

2. Installation
Bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
pip install -r requirements.txt
3. API Secrets
Create a .streamlit/secrets.toml file:

Ini, TOML
API_KEY = "YOUR_GOOGLE_GEMINI_API_KEY"
☁️ Deployment on Streamlit Cloud
The project is pre-configured for Streamlit Community Cloud. To ensure a successful deployment, two configuration files are included:

requirements.txt: Defines the Python environment.

packages.txt: Mandatory. It contains the word ffmpeg. This instructs the Streamlit server to install the FFmpeg binary at the system level before the app starts. Without this, Whisper will fail.

Cloud Deployment Steps:
Push your code to a GitHub repository.

Connect the repo to Streamlit Cloud.

In Advanced Settings > Secrets, paste your API_KEY.

Deploy!


💡 Final Tip
Ensure the template.pptx file is in your root directory. This file acts as the "canvas" for the PowerPoint generation; without it, the crear_pptx function will not have a base to build upon.
