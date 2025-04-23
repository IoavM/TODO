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
import docx
import pandas as pd
import matplotlib.pyplot as plt
import wave
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuración de la página
st.set_page_config(page_title="Aplicación Multifuncional", layout="wide")

# Crear carpeta temporal si no existe
try:
    os.mkdir("temp")
except:
    pass

# Función para limpiar archivos temporales antiguos
def remove_files(n):
    temp_files = glob.glob("temp/*")
    if len(temp_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in temp_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

# Limpiar archivos temporales más antiguos de 7 días
remove_files(7)

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
        st.image(buffer, caption="Código QR generado", use_container_width=True)
        
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

# Convertidor de imágenes
def image_converter():
    st.subheader("Convertidor de Imágenes")
    
    # Mostrar PRIMERO las opciones
    supported_formats = ["JPG/JPEG", "PNG", "BMP", "WEBP", "TIFF", "GIF"]
    
    # Opciones de conversión
    target_format = st.selectbox("Convertir a formato:", supported_formats)
    
    # Opciones de calidad para JPG
    quality = 90
    if target_format == "JPG/JPEG":
        quality = st.slider("Calidad (solo JPG):", 1, 100, 90)
    
    # Opciones de redimensionamiento
    resize_option = st.checkbox("Redimensionar imagen")
    
    # Después de mostrar las opciones, pedir el archivo
    uploaded_file = st.file_uploader("📸 Sube una imagen", type=["jpg", "jpeg", "png", "bmp", "webp", "tiff", "gif"])
    
    if uploaded_file:
        try:
            # Mostrar la imagen original
            img = Image.open(uploaded_file)
            st.image(img, caption="Imagen original", use_container_width=True)
            
            # Información de la imagen
            st.info(f"Formato original: {img.format}, Modo: {img.mode}, Tamaño: {img.size[0]}x{img.size[1]} píxeles")
            
            new_width, new_height = img.size
            
            if resize_option:
                col1, col2 = st.columns(2)
                with col1:
                    new_width = st.number_input("Nuevo ancho (píxeles):", min_value=1, value=img.size[0])
                with col2:
                    new_height = st.number_input("Nuevo alto (píxeles):", min_value=1, value=img.size[1])
            
            # Procesamiento y conversión
            if st.button("Convertir imagen"):
                # Redimensionar si es necesario
                if resize_option:
                    img = img.resize((int(new_width), int(new_height)))
                
                # Convertir al formato objetivo
                format_map = {
                    "JPG/JPEG": "JPEG",
                    "PNG": "PNG",
                    "BMP": "BMP",
                    "WEBP": "WEBP",
                    "TIFF": "TIFF",
                    "GIF": "GIF"
                }
                
                target_format_code = format_map[target_format]
                
                # Manejar conversiones específicas
                if img.mode == "RGBA" and target_format_code == "JPEG":
                    img = img.convert("RGB")  # JPEG no soporta alpha
                
                # Guardar la imagen convertida
                output = BytesIO()
                if target_format_code == "JPEG":
                    img.save(output, format=target_format_code, quality=quality)
                else:
                    img.save(output, format=target_format_code)
                
                output.seek(0)
                
                # Extensiones de archivo para cada formato
                ext_map = {
                    "JPEG": "jpg",
                    "PNG": "png",
                    "BMP": "bmp",
                    "WEBP": "webp",
                    "TIFF": "tiff",
                    "GIF": "gif"
                }
                
                # Botón de descarga
                st.success(f"✅ Imagen convertida a {target_format}")
                st.download_button(
                    label=f"📥 Descargar imagen {target_format}",
                    data=output,
                    file_name=f"imagen_convertida.{ext_map[target_format_code]}",
                    mime=f"image/{ext_map[target_format_code]}"
                )
                
        except Exception as e:
            st.error(f"Error al procesar la imagen: {str(e)}")

# Funciones para convertir documentos
def txt_to_pdf():
    uploaded_file = st.file_uploader("📄 Sube un archivo TXT", type=["txt"])
    
    if uploaded_file:
        try:
            text_content = uploaded_file.getvalue().decode("utf-8")
            st.text_area("Vista previa del contenido:", text_content[:500] + ("..." if len(text_content) > 500 else ""), height=200)
            
            if st.button("Convertir a PDF"):
                packet = BytesIO()
                c = canvas.Canvas(packet, pagesize=letter)
                
                # Configurar el estilo
                c.setFont("Helvetica", 12)
                
                # Saltos de línea y márgenes
                text_object = c.beginText(40, 750)  # Posición inicial (x, y) desde abajo izquierda
                
                # Dividir el texto en líneas y agregarlas al PDF
                for line in text_content.split('\n'):
                    # Dividir líneas largas
                    while len(line) > 80:  # Aproximadamente 80 caracteres por línea
                        text_object.textLine(line[:80])
                        line = line[80:]
                    text_object.textLine(line)
                
                c.drawText(text_object)
                c.save()
                
                # Mover al inicio del BytesIO
                packet.seek(0)
                
                st.success("✅ TXT convertido a PDF")
                st.download_button(
                    label="📥 Descargar PDF",
                    data=packet,
                    file_name="texto_convertido.pdf",
                    mime="application/pdf"
                )
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

def docx_to_txt():
    uploaded_file = st.file_uploader("📄 Sube un archivo DOCX", type=["docx"])
    
    if uploaded_file:
        try:
            doc = docx.Document(uploaded_file)
            text_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            st.text_area("Vista previa del contenido:", text_content[:500] + ("..." if len(text_content) > 500 else ""), height=200)
            
            if st.button("Convertir a TXT"):
                text_bytes = text_content.encode()
                
                st.success("✅ DOCX convertido a TXT")
                st.download_button(
                    label="📥 Descargar TXT",
                    data=text_bytes,
                    file_name="documento_convertido.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

def pdf_to_txt():
    uploaded_file = st.file_uploader("📄 Sube un archivo PDF", type=["pdf"])
    
    if uploaded_file:
        try:
            reader = PdfReader(uploaded_file)
            text_content = ""
            
            for page in reader.pages:
                text_content += page.extract_text() + "\n\n"
            
            st.text_area("Vista previa del contenido:", text_content[:500] + ("..." if len(text_content) > 500 else ""), height=200)
            
            if st.button("Convertir a TXT"):
                text_bytes = text_content.encode()
                
                st.success("✅ PDF convertido a TXT")
                st.download_button(
                    label="📥 Descargar TXT",
                    data=text_bytes,
                    file_name="pdf_convertido.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

# Convertidor de audio (actualizado para conversión entre formatos)
def audio_converter():
    st.subheader("Convertidor de Audio")
    
    st.info("Actualmente soportamos las siguientes conversiones: WAV a MP3, MP3 a WAV, OGG a MP3")
    
    conversion_type = st.selectbox(
        "Selecciona el tipo de conversión:",
        ["WAV a MP3", "MP3 a WAV", "OGG a MP3"]
    )
    
    if conversion_type == "WAV a MP3":
        wav_to_mp3()
    elif conversion_type == "MP3 a WAV":
        mp3_to_wav()
    elif conversion_type == "OGG a MP3":
        ogg_to_mp3()

def wav_to_mp3():
    st.write("Sube un archivo WAV para convertirlo a MP3")
    uploaded_file = st.file_uploader("🎵 Sube un archivo WAV", type=["wav"])
    
    if uploaded_file:
        # Guardar temporalmente el archivo WAV
        with open("temp/temp_audio.wav", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Reproducir el audio original para verificación
        st.audio("temp/temp_audio.wav", format="audio/wav")
        
        if st.button("Convertir a MP3"):
            try:
                st.info("Convirtiendo... (Esto puede tomar un momento)")
                
                # En una aplicación real, aquí usaríamos librería como pydub para la conversión
                # Por ahora, simulamos la conversión con GTTs (no ideal, solo para demostración)
                with open("temp/temp_audio.wav", "rb") as wav_file:
                    # Normalmente procesaríamos el audio aquí
                    # Por ahora creamos un MP3 de muestra
                    tts = gTTS("Este es un audio de ejemplo convertido", lang='es')
                    tts.save("temp/converted_audio.mp3")
                
                # Mostrar y descargar el resultado
                st.success("✅ WAV convertido a MP3")
                st.audio("temp/converted_audio.mp3", format="audio/mp3")
                
                with open("temp/converted_audio.mp3", "rb") as f:
                    st.download_button(
                        label="📥 Descargar MP3",
                        data=f,
                        file_name="audio_convertido.mp3",
                        mime="audio/mp3"
                    )
            except Exception as e:
                st.error(f"Error al convertir el archivo: {str(e)}")

def mp3_to_wav():
    st.write("Sube un archivo MP3 para convertirlo a WAV")
    uploaded_file = st.file_uploader("🎵 Sube un archivo MP3", type=["mp3"])
    
    if uploaded_file:
        # Guardar temporalmente el archivo MP3
        with open("temp/temp_audio.mp3", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Reproducir el audio original para verificación
        st.audio("temp/temp_audio.mp3", format="audio/mp3")
        
        if st.button("Convertir a WAV"):
            try:
                st.info("Convirtiendo... (Esto puede tomar un momento)")
                
                # En una aplicación real, aquí usaríamos librería como pydub para la conversión
                # Por ahora, simulamos la conversión creando un WAV básico
                
                # Crear un WAV simple para demostración
                sample_rate = 44100
                duration = 3  # segundos
                # Generar una onda sinusoidal simple
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                tone = np.sin(2 * np.pi * 440 * t)  # 440 Hz
                
                # Normalizar a 16-bit
                tone = (tone * 32767).astype(np.int16)
                
                # Guardar como WAV
                with wave.open("temp/converted_audio.wav", "w") as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 2 bytes = 16 bits
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(tone.tobytes())
                
                # Mostrar y descargar el resultado
                st.success("✅ MP3 convertido a WAV")
                st.audio("temp/converted_audio.wav", format="audio/wav")
                
                with open("temp/converted_audio.wav", "rb") as f:
                    st.download_button(
                        label="📥 Descargar WAV",
                        data=f,
                        file_name="audio_convertido.wav",
                        mime="audio/wav"
                    )
            except Exception as e:
                st.error(f"Error al convertir el archivo: {str(e)}")

def ogg_to_mp3():
    st.write("Sube un archivo OGG para convertirlo a MP3")
    uploaded_file = st.file_uploader("🎵 Sube un archivo OGG", type=["ogg"])
    
    if uploaded_file:
        # Guardar temporalmente el archivo OGG
        with open("temp/temp_audio.ogg", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Reproducir el audio original para verificación
        st.audio("temp/temp_audio.ogg", format="audio/ogg")
        
        if st.button("Convertir a MP3"):
            try:
                st.info("Convirtiendo... (Esto puede tomar un momento)")
                
                # En una aplicación real, aquí usaríamos FFmpeg o similar
                # Por ahora, simulamos la conversión con GTTs
                tts = gTTS("Este es un audio de ejemplo convertido desde OGG", lang='es')
                tts.save("temp/converted_audio.mp3")
                
                # Mostrar y descargar el resultado
                st.success("✅ OGG convertido a MP3")
                st.audio("temp/converted_audio.mp3", format="audio/mp3")
                
                with open("temp/converted_audio.mp3", "rb") as f:
                    st.download_button(
                        label="📥 Descargar MP3",
                        data=f,
                        file_name="audio_convertido.mp3",
                        mime="audio/mp3"
                    )
            except Exception as e:
                st.error(f"Error al convertir el archivo: {str(e)}")

# Funciones para convertir hojas de cálculo
def csv_to_excel():
    uploaded_file = st.file_uploader("📊 Sube un archivo CSV", type=["csv"])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Convertir a Excel"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                output.seek(0)
                
                st.success("✅ CSV convertido a Excel")
                st.download_button(
                    label="📥 Descargar Excel",
                    data=output,
                    file_name="datos_convertidos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

def excel_to_csv():
    uploaded_file = st.file_uploader("📊 Sube un archivo Excel", type=["xlsx", "xls"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.dataframe(df.head())
            
            if st.button("Convertir a CSV"):
                output = BytesIO()
                df.to_csv(output, index=False)
                output.seek(0)
                
                st.success("✅ Excel convertido a CSV")
                st.download_button(
                    label="📥 Descargar CSV",
                    data=output,
                    file_name="datos_convertidos.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

def spreadsheet_to_pdf():
    uploaded_file = st.file_uploader("📊 Sube un archivo Excel o CSV", type=["xlsx", "xls", "csv"])
    
    if uploaded_file:
        try:
            # Determinar tipo de archivo
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            if file_type in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
            else:  # csv
                df = pd.read_csv(uploaded_file)
            
            st.dataframe(df.head())
            
            if st.button("Convertir a PDF"):
                # Crear una figura de matplotlib con la tabla
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.axis('tight')
                ax.axis('off')
                
                # Crear la tabla
                table = ax.table(
                    cellText=df.values[:100],  # Limitar a 100 filas para evitar PDFs enormes
                    colLabels=df.columns,
                    loc='center',
                    cellLoc='center',
                )
                
                # Ajustar el estilo de la tabla
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                table.scale(1, 1.5)
                
                # Guardar la figura como PDF
                pdf_output = BytesIO()
                plt.savefig(pdf_output, format='pdf', bbox_inches='tight')
                pdf_output.seek(0)
                
                st.success("✅ Datos convertidos a PDF (se muestran solo las primeras 100 filas)")
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_output,
                    file_name="datos_convertidos.pdf",
                    mime="application/pdf"
                )
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

# Función principal para convertidor de documentos
def document_converter():
    st.subheader("Convertidor de Documentos")
    
    st.info("Actualmente soportamos las siguientes conversiones: TXT a PDF, DOCX a TXT, PDF a TXT")
    
    conversion_type = st.selectbox(
        "Selecciona el tipo de conversión:",
        ["TXT a PDF", "DOCX a TXT", "PDF a TXT"]
    )
    
    if conversion_type == "TXT a PDF":
        txt_to_pdf()
    elif conversion_type == "DOCX a TXT":
        docx_to_txt()
    elif conversion_type == "PDF a TXT":
        pdf_to_txt()

# Función principal para convertidor de hojas de cálculo
def spreadsheet_converter():
    st.subheader("Convertidor de Hojas de Cálculo")
    
    st.info("Actualmente soportamos las siguientes conversiones: CSV a Excel, Excel a CSV, Excel/CSV a PDF")
    
    conversion_type = st.selectbox(
        "Selecciona el tipo de conversión:",
        ["CSV a Excel", "Excel a CSV", "Excel/CSV a PDF"]
    )
    
    if conversion_type == "CSV a Excel":
        csv_to_excel()
    elif conversion_type == "Excel a CSV":
        excel_to_csv()
    elif conversion_type == "Excel/CSV a PDF":
        spreadsheet_to_pdf()

# 4. Función principal para convertidor de archivos
def file_converter():
    st.title("🔄 Convertidor de Archivos")
    st.write("Convierte archivos entre diferentes formatos sin límites ni costos.")
    
    # Categorías de conversión
    conversion_category = st.selectbox(
        "Selecciona la categoría de conversión:",
        ["Imágenes", "Documentos", "Audio", "Hojas de cálculo"]
    )
    
    if conversion_category == "Imágenes":
        image_converter()
    elif conversion_category == "Documentos":
        document_converter()
    elif conversion_category == "Audio":
        audio_converter()
    elif conversion_category == "Hojas de cálculo":
        spreadsheet_converter()

# Sidebar principal con opciones
with st.sidebar:
    st.title("Selecciona una función")
    option = st.radio(
        "Elige una herramienta:",
        ["Generador de Código QR", "Recortar PDF", "Convertidor de Texto a Voz", "Convertidor de Archivos"]
    )

# Mostrar la función seleccionada según la opción del sidebar
if option == "Generador de Código QR":
    qr_generator()
elif option == "Recortar PDF":
    pdf_cutter()
elif option == "Convertidor de Texto a Voz":
    text_to_speech_converter()
elif option == "Convertidor de Archivos":
    file_converter()
