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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

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
    prs = Presentation("template.pptx")

    # Patrón mejorado para capturar el bloque completo entre diapositivas
    pattern = r"---\s*SLIDE\s*\d+\s*---\s*(.*?)\s*(?=(?:---\s*SLIDE\s*\d+\s*---)|\Z)"
    slides = re.findall(pattern, texto_generado, flags=re.S)

    if not slides:
        slides = [s for s in re.split(r"---\s*SLIDE", texto_generado) if s.strip()]

    for slide_text in slides:
        lines = [l.strip() for l in slide_text.strip().splitlines() if l.strip()]
        if not lines:
            continue

        # El primer elemento es siempre el Título
        title_text = lines[0]

        # Identificamos dónde empiezan las notas para separar el cuerpo
        notes_idx = None
        for i, ln in enumerate(lines):
            if ln.lower().startswith(("notes", "notes_slide", "notes:")):
                notes_idx = i
                break

        # Extraemos el cuerpo (párrafo) y las notas
        if notes_idx is not None:
            body_content = "\n".join(lines[1:notes_idx])
            notes_text = "\n".join(lines[notes_idx + 1:])
        else:
            body_content = "\n".join(lines[1:])
            notes_text = ""

        # Usamos el layout 1 (Título y Objetos)
        slide = prs.slides.add_slide(prs.slide_layouts[1])

        # 1. Configurar Título (con tamaño controlado)
        if slide.shapes.title:
            slide.shapes.title.text = title_text
            for paragraph in slide.shapes.title.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(32) # Tamaño ideal para títulos largos

        # 2. Configurar Cuerpo (como un solo párrafo fluido)
        if len(slide.placeholders) > 1:
            tf = slide.placeholders[1].text_frame
            tf.clear()
            tf.word_wrap = True # Evita que el texto se salga horizontalmente
            tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE # Ajuste automático si sobra texto
            
            p = tf.paragraphs[0]
            p.text = body_content
            for run in p.runs:
                run.font.size = Pt(18) # Tamaño de lectura para párrafos extensos

        # 3. Notas del orador
        if notes_text:
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
    styles = getSampleStyleSheet()
    
    # Definimos un estilo para el cuerpo que permita párrafos largos
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,      # Espacio entre líneas
        alignment=0,     # Alineado a la izquierda
        spaceAfter=10
    )
    
    # Estilo para el título
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        spaceAfter=20
    )

    pattern = r"---\s*SLIDE\s*\d+\s*---\s*(.*?)\s*(?=(?:---\s*SLIDE\s*\d+\s*---)|\Z)"
    slides = re.findall(pattern, texto_generado, flags=re.S)

    if not slides:
        slides = [s for s in re.split(r"---\s*SLIDE", texto_generado) if s.strip()]

    for slide_text in slides:
        lines = [l.strip() for l in slide_text.splitlines() if l.strip()]
        if not lines:
            continue

        title_text = lines[0]
        
        # Separar notas del cuerpo
        notes_idx = None
        for i, ln in enumerate(lines):
            if ln.lower().startswith(("notes", "notes_slide", "notes:")):
                notes_idx = i
                break
        
        body_lines = lines[1:notes_idx] if notes_idx is not None else lines[1:]
        # Limpiamos posibles viñetas residuales y unimos en un solo párrafo
        body_text = " ".join([re.sub(r'^[\*\-\u2022]\s*', '', l) for l in body_lines])

        # Dibujar Título con ajuste automático
        p_title = Paragraph(title_text, title_style)
        # Le damos un ancho máximo (ancho de hoja menos márgenes)
        w_t, h_t = p_title.wrap(width - 2*inch, height)
        p_title.drawOn(c, 1*inch, height - 1.2 * inch - h_t)

        # Dibujar Cuerpo con ajuste automático
        p_body = Paragraph(body_text, body_style)
        w_b, h_b = p_body.wrap(width - 2*inch, height)
        # Se dibuja debajo del título dejando un margen
        p_body.drawOn(c, 1*inch, height - 1.5 * inch - h_t - h_b)

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
    MAX_FILE_SIZE = 30 * 1024 * 1024
    if Audio_fill.size > MAX_FILE_SIZE:
        st.error("The audio is too long or too short. Please upload a file shorter than 30 minutes. (MAX 30MB)")
        st.stop()
    with st.expander("Show audio"):
     st.audio(Audio_fill)

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
        Analyze the following audio transcription and generate a presentation based ONLY on its content:

        {resultado['text']}

        === REGLA DE IDIOMA (OBLIGATORIA) ===

        Detecta el idioma original de la transcripción.

        TODO el resultado (diapositivas y notas) DEBE estar escrito al 100% en ese mismo idioma.

        === REGLA DE ENFOQUE (AGENTE DE ANÁLISIS) ===
        • Actúa como un AGENTE ESTRATÉGICO que extrae conceptos y los organiza para una presentación corporativa o académica.
        • NO menciones al "usuario" ni digas "la transcripción dice". Simplemente presenta la información como hechos o pilares del proyecto.
        • Transforma las ideas breves en conceptos desarrollados.
        * Ejemplo: Si el audio menciona "villanos científicos", la diapositiva debe titularse "Naturaleza de la Oposición" y explicar en un párrafo la metodología y origen de esos antagonistas.

        === REGLAS DE GENERACIÓN ===
        • Crea una presentación con un MÍNIMO de 5 diapositivas.
        • Cada diapositiva debe representar un pilar o sección lógica del contenido.

        === ESTRUCTURA DE LA DIAPOSITIVA (OBLIGATORIA) ===

        --- SLIDE N ---

        Título (Directo y profesional)
        [Texto de la diapositiva]
        Escribe un párrafo de 4 a 6 líneas que explique detalladamente el concepto.
        PROHIBIDO EL USO DE VIÑETAS O LISTAS. El texto debe ser continuo y fluido.

        notes_slide:
        Escribe un guion profesional para el presentador. Debe profundizar en el porqué de ese concepto y cómo se conecta con el resto de la presentación, usando un lenguaje formal.

        === REGLAS DE FORMATO ===
        • SIN LISTAS DE PUNTOS. Solo prosa bien redactada.
        • NO incluyas introducciones como "Aquí tienes la presentación".
        • El resultado debe ser exclusivamente el contenido de las diapositivas.

        === REGLA DE RESPALDO ===
        Si la transcripción es muy corta, expande los puntos mencionados con deducciones lógicas profesionales para alcanzar las 5 diapositivas (ej. si menciona "historia larga", dedica una diapositiva a la "Estructura Narrativa y Alcance del Proyecto").

        Devuelve SOLO el contenido estructurado.
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
