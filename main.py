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

from docx2pdf import convert as docx2pdf_convert
from pdf2docx import Converter as PDF2DOCXConverter
import tempfile

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

# Sidebar con opciones
with st.sidebar:
    st.title("Selecciona una función")
    option = st.radio(
        "Elige una herramienta:",
        ["Generador de Código QR", "Recortar PDF", "Convertidor de Texto a Voz", "Convertidor de Archivos"]
    )
    st.write(f"Opción seleccionada: {option}")  # Debug: Muestra la opción seleccionada

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
    
    if st.button("Convertir a Audio"):
        if text:
            result, output_text = text_to_speech(text, tld, lg)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown(f"## Tu audio:")
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

# 4. Convertidor de archivos
def file_converter():
    try:
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
    except Exception as e:
        st.error(f"Error en la función file_converter: {str(e)}")

# Convertidor de imágenes
def image_converter():
    st.subheader("Convertidor de Imágenes")
    
    supported_formats = ["JPG/JPEG", "PNG", "BMP", "WEBP", "TIFF", "GIF"]
    
    uploaded_file = st.file_uploader("📸 Sube una imagen", type=["jpg", "jpeg", "png", "bmp", "webp", "tiff", "gif"])
    
    if uploaded_file:
        try:
            # Mostrar la imagen original
            img = Image.open(uploaded_file)
            st.image(img, caption="Imagen original", use_column_width=True)
            
            # Información de la imagen
            st.info(f"Formato original: {img.format}, Modo: {img.mode}, Tamaño: {img.size[0]}x{img.size[1]} píxeles")
            
            # Opciones de conversión
            target_format = st.selectbox("Convertir a formato:", supported_formats)
            
            # Opciones de calidad para JPG
            quality = 90
            if target_format == "JPG/JPEG":
                quality = st.slider("Calidad (solo JPG):", 1, 100, 90)
            
            # Opciones de redimensionamiento
            resize_option = st.checkbox("Redimensionar imagen")
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

# Convertidor de documentos
# Añade esto a tus imports
from docx2pdf import convert as docx2pdf_convert
from pdf2docx import Converter as PDF2DOCXConverter
import tempfile

# Modificar la función document_converter para incluir las nuevas opciones
def document_converter():
    st.subheader("Convertidor de Documentos")
    
    st.info("Actualmente soportamos las siguientes conversiones: TXT a PDF, DOCX a TXT, PDF a TXT, DOCX a PDF, PDF a DOCX")
    
    conversion_type = st.selectbox(
        "Selecciona el tipo de conversión:",
        ["TXT a PDF", "DOCX a TXT", "PDF a TXT", "DOCX a PDF", "PDF a DOCX"]
    )
    
    if conversion_type == "TXT a PDF":
        txt_to_pdf()
    elif conversion_type == "DOCX a TXT":
        docx_to_txt()
    elif conversion_type == "PDF a TXT":
        pdf_to_txt()
    elif conversion_type == "DOCX a PDF":
        docx_to_pdf()
    elif conversion_type == "PDF a DOCX":
        pdf_to_docx()

# Añadir estas nuevas funciones

def docx_to_pdf():
    uploaded_file = st.file_uploader("📄 Sube un archivo DOCX", type=["docx"])
    
    if uploaded_file:
        try:
            # Crear directorio temporal
            temp_dir = tempfile.TemporaryDirectory()
            input_path = f"{temp_dir.name}/input.docx"
            output_path = f"{temp_dir.name}/output.pdf"
            
            # Guardar el archivo subido
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Realizar la conversión
            if st.button("Convertir a PDF"):
                with st.spinner("⏳ Convirtiendo DOCX a PDF..."):
                    docx2pdf_convert(input_path, output_path)
                
                # Leer el archivo convertido
                with open(output_path, "rb") as f:
                    pdf_bytes = f.read()
                
                st.success("✅ DOCX convertido a PDF")
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_bytes,
                    file_name="documento_convertido.pdf",
                    mime="application/pdf"
                )
                
                # Opcional: previsualizar primera página
                try:
                    reader = PdfReader(output_path)
                    if len(reader.pages) > 0:
                        st.write("Vista previa (primera página):")
                        st.write(reader.pages[0].extract_text()[:500] + "...")
                except:
                    pass
                    
            # Limpiar
            temp_dir.cleanup()
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")
            st.info("Para la conversión de DOCX a PDF, asegúrate de tener LibreOffice o Microsoft Word instalado en el servidor.")

def pdf_to_docx():
    uploaded_file = st.file_uploader("📄 Sube un archivo PDF", type=["pdf"])
    
    if uploaded_file:
        try:
            # Crear directorio temporal
            temp_dir = tempfile.TemporaryDirectory()
            input_path = f"{temp_dir.name}/input.pdf"
            output_path = f"{temp_dir.name}/output.docx"
            
            # Guardar el archivo subido
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Opciones de conversión
            max_pages = 50  # Limite por defecto para evitar archivos muy grandes
            
            # Verificar número de páginas
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            
            st.info(f"Este PDF tiene {total_pages} páginas.")
            
            if total_pages > max_pages:
                convert_all = st.checkbox(f"El PDF tiene más de {max_pages} páginas. ¿Convertir todas? (puede tomar tiempo)")
                pages_to_convert = total_pages if convert_all else max_pages
            else:
                pages_to_convert = total_pages
            
            # Realizar la conversión
            if st.button("Convertir a DOCX"):
                with st.spinner(f"⏳ Convirtiendo PDF a DOCX ({pages_to_convert} páginas)..."):
                    # Configurar el convertidor
                    cv = PDF2DOCXConverter(input_path)
                    # Convertir por páginas
                    cv.convert(output_path, start=0, end=pages_to_convert)
                    # Cerrar el convertidor
                    cv.close()
                
                # Leer el archivo convertido
                with open(output_path, "rb") as f:
                    docx_bytes = f.read()
                
                st.success("✅ PDF convertido a DOCX")
                st.download_button(
                    label="📥 Descargar DOCX",
                    data=docx_bytes,
                    file_name="pdf_convertido.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
                # Opcional: mostrar vista previa
                try:
                    doc = docx.Document(output_path)
                    preview_text = "\n".join([p.text for p in doc.paragraphs][:20])
                    st.text_area("Vista previa del contenido:", preview_text[:500] + ("..." if len(preview_text) > 500 else ""), height=200)
                except:
                    pass
                    
            # Limpiar
            temp_dir.cleanup()
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")
# Convertidor de audio (funcionalidad básica)
def audio_converter():
    st.subheader("Convertidor de Audio")
    st.write("Convierte archivos de audio entre diferentes formatos.")
    
    # Para trabajar con archivos de audio necesitaremos la biblioteca pydub
    # Muestra un mensaje si no está instalada
    try:
        from pydub import AudioSegment
        pydub_installed = True
    except ImportError:
        st.error("Se requiere la biblioteca 'pydub' para la conversión de audio. Instálala con: pip install pydub")
        st.info("También necesitarás FFmpeg instalado en tu sistema para la conversión de formatos.")
        pydub_installed = False
        return
    
    if pydub_installed:
        # Formatos soportados
        supported_formats = ["mp3", "wav", "ogg", "flac", "aac", "m4a"]
        
        uploaded_file = st.file_uploader("🎵 Sube un archivo de audio", type=supported_formats)
        
        if uploaded_file:
            # Obtener el formato original
            original_format = uploaded_file.name.split('.')[-1].lower()
            
            # Guardar temporalmente el archivo subido
            with open(f"temp/temp_audio.{original_format}", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Cargar el audio con pydub
            try:
                audio = AudioSegment.from_file(f"temp/temp_audio.{original_format}", format=original_format)
                
                # Información del audio
                duration_seconds = len(audio) / 1000
                channels = audio.channels
                sample_width = audio.sample_width
                frame_rate = audio.frame_rate
                
                st.success("✅ Audio cargado correctamente")
                st.audio(uploaded_file, format=f"audio/{original_format}")
                
                st.info(f"Información del audio:\n" +
                       f"- Duración: {int(duration_seconds // 60)}:{int(duration_seconds % 60):02d} (min:seg)\n" +
                       f"- Canales: {channels} ({'Estéreo' if channels == 2 else 'Mono'})\n" +
                       f"- Profundidad de bits: {sample_width * 8} bits\n" +
                       f"- Frecuencia de muestreo: {frame_rate} Hz")
                
                # Opciones de conversión
                target_formats = [fmt for fmt in supported_formats if fmt != original_format]
                target_format = st.selectbox("Convertir a formato:", target_formats)
                
                # Opciones adicionales
                st.subheader("Opciones adicionales")
                
                # Ajuste de volumen
                volume_adjustment = st.slider("Ajuste de volumen (dB):", -20, 20, 0)
                
                # Recortar audio
                trim_audio = st.checkbox("Recortar audio")
                start_time, end_time = 0, duration_seconds
                
                if trim_audio:
                    col1, col2 = st.columns(2)
                    with col1:
                        start_time = st.number_input("Tiempo de inicio (segundos):", min_value=0.0, max_value=duration_seconds-1, value=0.0, step=0.1)
                    with col2:
                        end_time = st.number_input("Tiempo final (segundos):", min_value=start_time+0.1, max_value=duration_seconds, value=duration_seconds, step=0.1)
                
                if st.button("Convertir audio"):
                    # Aplicar ajustes
                    processed_audio = audio
                    
                    # Ajustar volumen si es necesario
                    if volume_adjustment != 0:
                        processed_audio = processed_audio + volume_adjustment
                    
                    # Recortar si es necesario
                    if trim_audio:
                        processed_audio = processed_audio[int(start_time*1000):int(end_time*1000)]
                    
                    # Guardar en el nuevo formato
                    output_file = f"temp/converted_audio.{target_format}"
                    processed_audio.export(output_file, format=target_format)
                    
                    # Leer el archivo convertido
                    with open(output_file, "rb") as f:
                        converted_audio_bytes = f.read()
                    
                    st.success(f"✅ Audio convertido a {target_format.upper()}")
                    
                    # Reproducir el audio convertido
                    st.audio(converted_audio_bytes, format=f"audio/{target_format}")
                    
                    # Botón de descarga
                    st.download_button(
                        label=f"📥 Descargar audio {target_format.upper()}",
                        data=converted_audio_bytes,
                        file_name=f"audio_convertido.{target_format}",
                        mime=f"audio/{target_format}"
                    )
                    
            except Exception as e:
                st.error(f"Error al procesar el archivo de audio: {str(e)}")
                st.info("Asegúrate de que FFmpeg esté instalado correctamente en tu sistema.")
                
# Convertidor de hojas de cálculo
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

# Mostrar la función seleccionada según la opción del sidebar
if option == "Generador de Código QR":
    qr_generator()
elif option == "Recortar PDF":
    pdf_cutter()
elif option == "Convertidor de Texto a Voz":
    text_to_speech_converter()
elif option == "Convertidor de Archivos":
    try:
        file_converter()
    except Exception as e:
        st.error(f"Error al cargar el convertidor de archivos: {str(e)}")
else:
    st.error(f"Opción no reconocida: {option}")
