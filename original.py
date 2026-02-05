# ======================================================================================================================
# LIBRARIES & ENVIRONMENT
# ======================================================================================================================

import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = PROJECT_DIR + os.pathsep + os.environ.get("PATH", "")

import streamlit as st
import whisper
import google.generativeai as GenAI

from pptx import Presentation
from io import BytesIO
from pptx.util import Pt
from pptx.enum.text import MSO_AUTO_SIZE


from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

import re


def load_whisper():
    return whisper.load_model("base")



# ======================================================================================================================
# PAGE CONFIG & UI HEADER
# ======================================================================================================================

st.set_page_config(page_title="Gen", page_icon="🪄")

st.markdown(
    """
    <h1 style="
        color: #FFFFFF;
        text-align: center;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.7);
    ">
    🪄 𝑻𝒓𝒂𝒏𝒔𝒄𝒓𝒊𝒑𝒕𝒊𝒐𝒏 & 𝑺𝒍𝒊𝒅𝒆 𝑪𝒓𝒆𝒂𝒕𝒐𝒓
    </h1>
    """,
    unsafe_allow_html=True
)


# ======================================================================================================================
# BACKGROUND STYLING
# ======================================================================================================================

Url_Imagen = "https://i.pinimg.com/originals/cf/a2/39/cfa239195d194b724a9d38362859a1af.jpg"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{Url_Imagen}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    .main {{
        background-color: rgba(0, 0, 0, 0.45);
        padding: 20px;
        border-radius: 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ======================================================================================================================
# API CONFIGURATION
# ======================================================================================================================

GenAI.configure(api_key=st.secrets["API_KEY"])


# ======================================================================================================================
# POWERPOINT CREATION FUNCTION
# ======================================================================================================================

def crear_pptx(texto_generado):
    prs = Presentation()

    pattern = r"---\s*SLIDE\s*\d+\s*---\s*(.*?)\s*(?=(?:---\s*SLIDE\s*\d+\s*---)|\Z)"
    slides = re.findall(pattern, texto_generado, flags=re.S)

    if not slides:
        slides = [s for s in re.split(r"---\s*SLIDE", texto_generado) if s.strip()]

    for slide_text in slides:
        lines = [l.strip() for l in slide_text.strip().splitlines() if l.strip()]
        if not lines:
            continue

        title = lines[0]

        notes_idx = None
        for i, ln in enumerate(lines[1:], start=1):
            if ln.lower().startswith(("notes", "notes_slide", "notes:")):
                notes_idx = i
                break

        if notes_idx is not None:
            bullets_lines = lines[1:notes_idx]
            notes_lines = lines[notes_idx + 1:]
        else:
            bullets_lines = lines[1:]
            notes_lines = []

        bullets = [re.sub(r'^[\*\-\u2022]\s*', '', b) for b in bullets_lines]

        slide = prs.slides.add_slide(prs.slide_layouts[1])

        if slide.shapes.title:
            slide.shapes.title.text = title

        if len(slide.placeholders) > 1:
            tf = slide.placeholders[1].text_frame
            tf.clear()
            tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE

            if bullets:
                p = tf.paragraphs[0]
                p.text = bullets[0]
                p.level = 0
                for run in p.runs:
                    run.font.size = Pt(20)

                for b in bullets[1:]:
                    p = tf.add_paragraph()
                    p.text = b
                    p.level = 0
                    for run in p.runs:
                        run.font.size = Pt(18)

        notes_text = "\n".join(notes_lines if notes_lines else bullets)

        try:
            slide.notes_slide.notes_text_frame.text = notes_text
        except Exception:
            pass

    pptx_io = BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()

# ======================================================================================================================
# POWERPOINT CREATION FUNCTION
# ======================================================================================================================

def crear_pdf(texto_generado):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    pattern = r"---\s*SLIDE\s*\d+\s*---\s*(.*?)\s*(?=(?:---\s*SLIDE\s*\d+\s*---)|\Z)"
    slides = re.findall(pattern, texto_generado, flags=re.S)

    if not slides:
        slides = [s for s in re.split(r"---\s*SLIDE", texto_generado) if s.strip()]

    for slide_text in slides:
        lines = [l.strip() for l in slide_text.splitlines() if l.strip()]
        if not lines:
            continue

        title = lines[0]

        bullets = []
        for line in lines[1:]:
            if line.lower().startswith("notes"):
                break
            bullets.append(re.sub(r'^[\*\-\u2022]\s*', '', line))

        y = height - 1.2 * inch

        c.setFont("Helvetica-Bold", 20)
        c.drawString(1 * inch, y, title)
        y -= 0.6 * inch

        c.setFont("Helvetica", 14)
        for bullet in bullets:
            c.drawString(1.2 * inch, y, f"• {bullet}")
            y -= 0.35 * inch

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# ======================================================================================================================
# AUDIO UPLOAD & TRANSCRIPTION
# ======================================================================================================================
audio_Recorded = st.audio_input("𝑹𝒆𝒄𝒐𝒓𝒅 𝒚𝒐𝒖𝒓 𝒂𝒖𝒅𝒊𝒐")
audio_Fill = st.file_uploader(
    "𝑼𝒑𝒍𝒐𝒂𝒅 𝒚𝒐𝒖𝒓 𝒂𝒖𝒅𝒊𝒐",
    type=["mp3", "mp4", "opus", "wav", "m4a"]
)
Audio_fill = audio_Fill or audio_Recorded

if Audio_fill is not None:
    with st.expander("Show audio"):
     st.audio(Audio_fill)

    MAX_FILE_SIZE = 10 * 1024 * 1024

    if Audio_fill.size > MAX_FILE_SIZE:
        st.error("The audio is too long or too short. Please upload a file shorter than 3 minutes. (MAX 10MB)")
        st.stop()

    with open("temp_audio.wav", "wb") as f:
        f.write(Audio_fill.getbuffer())

    with st.spinner("Whisper is processing your audio"):
        modelo_whisper = load_whisper()
        resultado = modelo_whisper.transcribe("temp_audio.wav")


    with st.expander("Show transcription"):
        st.write(resultado["text"])


# ======================================================================================================================
# GENERATIVE SLIDES
# ======================================================================================================================

if Audio_fill is not None and st.button("✨ Generative Slides"):

    with st.spinner("Gemini is creating your slides..."):
        modelo_gemini = GenAI.GenerativeModel('models/gemini-2.5-flash')

        instruction = f"""
            Analyze the audio transcript: {resultado['text']} and generate ONLY clearly separated slides following these STRICT rules.

            !!! CRITICAL: LANGUAGE ENFORCEMENT !!!
            1. FIRST, analyze the input text to identify the source language exactly.
            2. YOUR OUTPUT MUST BE 100% IN THAT IDENTIFIED SOURCE LANGUAGE.
            3. IF the audio is in English -> Generate slides/notes in ENGLISH.
            4. IF the audio is in French -> Generate slides/notes in FRENCH.
            5. DO NOT translate to Spanish unless the audio is actually in Spanish.
            6. IGNORE the language of these instructions; follow ONLY the language of the transcript.

            === BEGIN INSTRUCTIONS ===

            1. TRANSCRIPTION
            Include the complete transcription of the audio.
            Write it ONLY in the original source language.
            Place it at the beginning under the heading:
            === TRANSCRIPTION ===

            2. INSTRUCTION DETECTION
            Determine whether the audio contains a clear instruction to create content.

            3. IF A CLEAR INSTRUCTION EXISTS
            Generate a presentation with a MINIMUM of 5 SLIDES.
            Each slide must be clearly separated and numbered.
            Each slide must represent a distinct idea or part of the requested content.

            Inside each slide:
            First line: Short Title
            Following lines: Bullet-point content only

            Use EXACTLY this separator:
            --- SLIDE N ---

            4. SLIDE STRUCTURE (MANDATORY)
            Each slide MUST follow this exact internal structure:

            Title
            • Bullet point
            • Bullet point

            notes_slide:
            Full, natural speaker notes written as if a real presenter were explaining the slide aloud.
            Notes must expand the slide content and provide context, explanations, or examples.
            *** THE NOTES MUST BE IN THE SAME LANGUAGE AS THE TRANSCRIPT ***

            5. IF NO CLEAR INSTRUCTION EXISTS
            Generate ONLY ONE slide.
            Clearly state (in the source language) that an explicit instruction is required in the audio.
            That slide MUST also include notes_slide.

            6. FORMAT RESTRICTIONS
            Speaker notes must appear ONLY inside notes_slide.
            Do NOT place notes in the slide body.
            Do NOT add explanations, comments, or text outside the defined structure.
            Output must be strictly structured for PowerPoint slide + notes usage.
        """

        answer = modelo_gemini.generate_content(instruction)


    with st.expander("Show Content"):
        st.write(answer.text)

    pptx_data = crear_pptx(answer.text)
    pdf_data = crear_pdf(answer.text)

    st.download_button(
        label="🚀 DOWNLOAD YOUR POWERPOINT",
        data=pptx_data,
        file_name="Presentation.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True
    )


    st.download_button(
    label="📄 DOWNLOAD PDF",
    data=pdf_data,
    file_name="Presentation.pdf",
    mime="application/pdf",
    use_container_width=True
)


    st.balloons()

    if os.path.exists("temp_audio.wav"):
        os.remove("temp_audio.wav")

