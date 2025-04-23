# Primero, agregar estas importaciones en la parte superior del archivo
# Junto con tus otras importaciones:
from pdf2docx import Converter
from docx2pdf import convert

# Luego, añadir estas dos nuevas funciones:

def pdf_to_docx():
    uploaded_file = st.file_uploader("📄 Sube un archivo PDF", type=["pdf"])
    
    if uploaded_file:
        try:
            # Guardar temporalmente el archivo PDF
            pdf_path = f"temp/temp_file_{int(time.time())}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            if st.button("Convertir a DOCX"):
                # Crear el nombre del archivo de salida
                docx_path = pdf_path.replace(".pdf", ".docx")
                
                # Convertir PDF a DOCX
                st.info("Convirtiendo PDF a DOCX... (Esto puede tomar un momento)")
                
                # Usar el convertidor
                cv = Converter(pdf_path)
                cv.convert(docx_path)
                cv.close()
                
                # Mostrar éxito y botón de descarga
                st.success("✅ PDF convertido a DOCX")
                
                with open(docx_path, "rb") as f:
                    docx_bytes = f.read()
                    
                st.download_button(
                    label="📥 Descargar DOCX",
                    data=docx_bytes,
                    file_name="documento_convertido.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
                # Limpiar archivos temporales
                try:
                    os.remove(pdf_path)
                    os.remove(docx_path)
                except:
                    pass
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

def docx_to_pdf():
    uploaded_file = st.file_uploader("📄 Sube un archivo DOCX", type=["docx"])
    
    if uploaded_file:
        try:
            # Guardar temporalmente el archivo DOCX
            docx_path = f"temp/temp_file_{int(time.time())}.docx"
            with open(docx_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            if st.button("Convertir a PDF"):
                # Crear el nombre del archivo de salida
                pdf_path = docx_path.replace(".docx", ".pdf")
                
                # Convertir DOCX a PDF
                st.info("Convirtiendo DOCX a PDF... (Esto puede tomar un momento)")
                
                # Usar docx2pdf para la conversión
                convert(docx_path, pdf_path)
                
                # Mostrar éxito y botón de descarga
                st.success("✅ DOCX convertido a PDF")
                
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_bytes,
                    file_name="documento_convertido.pdf",
                    mime="application/pdf"
                )
                
                # Limpiar archivos temporales
                try:
                    os.remove(docx_path)
                    os.remove(pdf_path)
                except:
                    pass
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

# Ahora, modifica la función document_converter() para incluir estas nuevas opciones:

def document_converter():
    st.subheader("Convertidor de Documentos")
    
    st.info("Actualmente soportamos las siguientes conversiones: TXT a PDF, DOCX a TXT, PDF a TXT, PDF a DOCX, DOCX a PDF")
    
    conversion_type = st.selectbox(
        "Selecciona el tipo de conversión:",
        ["TXT a PDF", "DOCX a TXT", "PDF a TXT", "PDF a DOCX", "DOCX a PDF"]
    )
    
    if conversion_type == "TXT a PDF":
        txt_to_pdf()
    elif conversion_type == "DOCX a TXT":
        docx_to_txt()
    elif conversion_type == "PDF a TXT":
        pdf_to_txt()
    elif conversion_type == "PDF a DOCX":
        pdf_to_docx()
    elif conversion_type == "DOCX a PDF":
        docx_to_pdf()
