¡Perfecto! Aquí tienes el archivo README.md completo, diseñado para que destaque en tu perfil de GitHub. Incluye secciones de arquitectura, configuración, despliegue y hasta una guía de "cómo funciona".

Copia y pega todo el bloque de abajo:

🪄 AI Transcription & Slide Creator
Turn your voice into a professional presentation in seconds. This application records or accepts audio, transcribes it locally using OpenAI's Whisper, analyzes the content with Google Gemini, and automatically generates a downloadable PowerPoint (.pptx) and PDF with structured slides and speaker notes.

🌟 Key Features
🎙️ Audio Flexibility: Record directly in the browser or upload files (mp3, wav, m4a, etc.).

🧠 Local Intelligence: Uses OpenAI Whisper (Base Model) for high-accuracy, privacy-focused transcription.

✨ Generative AI: Powered by Google Gemini 2.5 Flash to structure unstructured speech into logical slides (Title + Content + Speaker Notes).

🌍 Smart Language Detection: Automatically detects the audio language (English, Spanish, French, etc.) and generates the presentation and UI labels in the matching language.

📊 Dual Export: Download your deck as an editable PowerPoint (.pptx) or a ready-to-print PDF.

🎨 Custom Styling: Custom fonts, background styling, and layout handling for a corporate look.

🛠️ Tech Stack
Frontend: Streamlit

AI Models:

Audio-to-Text: openai-whisper

Text-to-Content: google-generativeai (Gemini API)

Document Generation:

python-pptx (for PowerPoint)

reportlab (for PDF)

🚀 Installation & Local Setup
1. Prerequisites
Python 3.9+

FFmpeg installed on your system (Required for Whisper).

Mac: brew install ffmpeg

Windows: choco install ffmpeg

Linux: sudo apt install ffmpeg

2. Setup
Bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Install dependencies
pip install -r requirements.txt
3. API Configuration
Get your key from Google AI Studio.

Create a file .streamlit/secrets.toml:

Ini, TOML
API_KEY = "YOUR_GOOGLE_GEMINI_API_KEY_HERE"
☁️ Deployment on Streamlit Cloud
This project is optimized to run on Streamlit Community Cloud. To deploy it successfully, you must ensure two files are in your root folder:

1. Mandatory Files for Cloud
requirements.txt: List of Python libraries.

Plaintext
streamlit
openai-whisper
google-generativeai
python-pptx
reportlab
setuptools
packages.txt: This is essential. It tells the Streamlit server to install the ffmpeg system binary, without which Whisper will fail.

Plaintext
ffmpeg
2. Cloud Secrets Setup
Do not upload your secrets.toml to GitHub. Instead:

Go to your app settings on the Streamlit Cloud Dashboard.

Find the Secrets section.

Paste your API key there:

Ini, TOML
API_KEY = "your_real_key_here"
🧠 How it Works
Transcription: The audio is processed by Whisper, which identifies the language and converts speech to text.

Strategic Analysis: The text is sent to Gemini with a specialized "Strategic Consultant" prompt. It requests a structure of exactly 5 slides with professional prose (no bullet points) and speaker notes.

Dynamic Rendering: * The script identifies the language code from Whisper (e.g., es, en).

It maps the language to the correct label for speaker notes (e.g., "NOTAS DE ORADOR" or "SPEAKER NOTES").

It injects the text into a template.pptx file.

Export: The user receives two download buttons for the generated files.

🤝 Contributing
Feel free to fork this project, open issues, or submit pull requests to improve the prompt engineering or the PDF styling!
