import streamlit as st
import qrcode
from PIL import Image
import io
import os
import time
import glob
import base64
from gtts import gTTS
from pypdf import PdfReader, PdfWriter
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Aplicación Multifuncional", layout="wide")

# Crear carpeta temporal si no existe
try:
    os.mkdir("temp")
except:
    pass

# Función para limpiar archivos temporales antiguos
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

# Limpiar archivos temporales más antiguos de 7 días
remove_files(7)

# Sidebar con opciones
with st.sidebar:
    st.title("Selecciona una función")
    option = st.radio(
        "Elige una herramienta:",
        ["Generador de Código QR", "Recortar PDF", "Convertidor de Texto a Voz"]
    )

# 1. Generador de código QR
def qr_generator():
    st.title("Generador de Código QR")
    # Entrada del texto para generar el QR
    qr_text = st.text_input("Introduce el texto o enlace para generar el código QR")
    
    if qr_text:
        # Crear código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        
        # Convertir el código QR en imagen
        img = qr.make_image(fill='black', back_color='white')
        
        # Guardar la imagen en un buffer de memoria
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)  # Reiniciar el puntero del buffer al inicio
        
        # Mostrar la imagen en Streamlit
        st.image(buffer, caption="Código QR generado", use_column_width=True)
        
        # Botón de descarga
        st.download_button(
            label="Descargar código QR",
            data=buffer,
            file_name="codigo_qr.png",
            mime="image/png"
        )

# 2. Recortar PDF
def pdf_cutter():
    st.title("✂️ Recortar un PDF por páginas")
    st.write("Carga un archivo PDF y selecciona el rango de páginas que quieres extraer.")
    
    uploaded_file = st.file_uploader("📄 Cargar PDF", type="pdf")
    
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        st.info(f"Este PDF tiene {total_pages} páginas.")
        
        start_page = st.number_input("Página inicial", min_value=1, max_value=total_pages, value=1)
        end_page = st.number_input("Página final", min_value=1, max_value=total_pages, value=total_pages)
        
        if start_page > end_page:
            st.error("⚠️ La página inicial no puede ser mayor que la final.")
        else:
            if st.button("Recortar PDF"):
                writer = PdfWriter()
                for i in range(start_page - 1, end_page):
                    writer.add_page(reader.pages[i])
                
                output = BytesIO()
                writer.write(output)
                output.seek(0)
                
                st.success("✅ PDF recortado listo para descargar")
                st.download_button(
                    label="📥 Descargar PDF recortado",
                    data=output,
                    file_name="pdf_recortado.pdf",
                    mime="application/pdf"
                )

# 3. Convertidor de texto a voz
def text_to_speech_converter():
    st.title("Conversión de Texto a Audio")
    
    with st.sidebar:
        st.subheader("Escribe y/o selecciona texto para ser escuchado.")
    
    # Entrada de texto
    text = st.text_area("Ingrese el texto a escuchar.")
    
    # Selección de idioma
    option_lang = st.selectbox("Selecciona el lenguaje", ("Español", "English"))
    
    if option_lang == "Español":
        lg = 'es'
    if option_lang == "English":
        lg = 'en'
    
    tld = 'com'
    
    def text_to_speech(text, tld, lg):
        tts = gTTS(text, lang=lg)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        
        # Limpiar nombre de archivo
        my_file_name = ''.join(e for e in my_file_name if e.isalnum() or e == ' ')
        my_file_name = my_file_name.replace(' ', '_')
        if not my_file_name:
            my_file_name = "audio"
            
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, text
    
    if st.button("convertir a Audio"):
        if text:
            result, output_text = text_to_speech(text, tld, lg)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown(f"## Tú audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
            
            with open(f"temp/{result}.mp3", "rb") as f:
                data = f.read()
                
            def get_binary_file_downloader_html(bin_file, file_label='File'):
                bin_str = base64.b64encode(data).decode()
                href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
                return href
                
            st.markdown(get_binary_file_downloader_html(f"temp/{result}.mp3", file_label="Audio File"), unsafe_allow_html=True)
        else:
            st.warning("Por favor, ingresa algún texto para convertir a audio.")

# Mostrar la función seleccionada según la opción del sidebar
if option == "Generador de Código QR":
    qr_generator()
elif option == "Recortar PDF":
    pdf_cutter()
elif option == "Convertidor de Texto a Voz":
    text_to_speech_converter()
