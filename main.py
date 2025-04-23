# Para PDF a DOCX, podemos usar una combinación de PyPDF2 y python-docx
# Para DOCX a PDF, podemos usar python-docx con reportlab

# Añade estas importaciones al principio del archivo
from pypdf import PdfReader
import docx
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Función alternativa para PDF a DOCX
def pdf_to_docx():
    uploaded_file = st.file_uploader("📄 Sube un archivo PDF", type=["pdf"])
    
    if uploaded_file:
        try:
            # Leer el PDF
            reader = PdfReader(uploaded_file)
            
            # Mostrar información sobre el PDF
            st.info(f"El PDF tiene {len(reader.pages)} páginas.")
            
            # Vista previa del contenido de la primera página
            if len(reader.pages) > 0:
                text_preview = reader.pages[0].extract_text()[:500]
                st.text_area("Vista previa del contenido (primera página):", text_preview + ("..." if len(text_preview) == 500 else ""), height=200)
            
            if st.button("Convertir a DOCX"):
                # Crear un nuevo documento de Word
                doc = Document()
                
                # Extraer texto de cada página del PDF y añadirlo al documento
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if i > 0:  # Agregar un salto de página después de cada página excepto la última
                        doc.add_paragraph()
                    
                    # Dividir el texto en párrafos y agregarlos al documento
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            doc.add_paragraph(para)
                
                # Guardar el documento en memoria
                docx_buffer = io.BytesIO()
                doc.save(docx_buffer)
                docx_buffer.seek(0)
                
                # Botón de descarga
                st.success("✅ PDF convertido a DOCX (solo texto)")
                st.warning("Nota: Esta conversión solo incluye texto, no conserva imágenes o formato complejo.")
                
                st.download_button(
                    label="📥 Descargar DOCX",
                    data=docx_buffer,
                    file_name="pdf_convertido.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

# Función alternativa para DOCX a PDF
def docx_to_pdf():
    uploaded_file = st.file_uploader("📄 Sube un archivo DOCX", type=["docx"])
    
    if uploaded_file:
        try:
            # Leer el documento DOCX
            doc = docx.Document(uploaded_file)
            
            # Mostrar vista previa del contenido
            text_preview = "\n".join([para.text for para in doc.paragraphs][:10])
            st.text_area("Vista previa del contenido:", text_preview + ("..." if len(doc.paragraphs) > 10 else ""), height=200)
            
            if st.button("Convertir a PDF"):
                # Crear PDF en memoria
                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=letter)
                width, height = letter
                
                # Configurar fuente
                c.setFont("Helvetica", 12)
                
                # Variables para controlar la posición del texto
                y = height - 50  # Comenzar desde arriba
                line_height = 14
                page_number = 1
                
                # Procesar cada párrafo
                for para in doc.paragraphs:
                    if para.text.strip():
                        # Dividir párrafos largos
                        text = para.text
                        
                        # Calcular ancho aproximado (esto es una aproximación simple)
                        max_width = width - 100  # Margen
                        
                        # Dividir texto largo en líneas
                        words = text.split()
                        lines = []
                        current_line = []
                        
                        for word in words:
                            # Añadir palabra si la línea no es muy larga
                            test_line = " ".join(current_line + [word])
                            if len(test_line) * 7 < max_width:  # Aproximación de ancho
                                current_line.append(word)
                            else:
                                # Guardar línea actual y comenzar una nueva
                                if current_line:
                                    lines.append(" ".join(current_line))
                                current_line = [word]
                        
                        # Añadir última línea si existe
                        if current_line:
                            lines.append(" ".join(current_line))
                        
                        # Dibujar líneas
                        for line in lines:
                            if y < 50:  # Si llegamos al final de la página
                                c.drawString(width - 50, 20, str(page_number))
                                c.showPage()
                                page_number += 1
                                y = height - 50
                                c.setFont("Helvetica", 12)
                            
                            c.drawString(50, y, line)
                            y -= line_height
                        
                        # Espacio extra después de cada párrafo
                        y -= 10
                
                # Añadir número de página a la última página
                c.drawString(width - 50, 20, str(page_number))
                c.save()
                pdf_buffer.seek(0)
                
                # Botón de descarga
                st.success("✅ DOCX convertido a PDF")
                st.warning("Nota: Esta conversión es básica y puede no preservar todo el formato original.")
                
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_buffer,
                    file_name="docx_convertido.pdf",
                    mime="application/pdf"
                )
                
        except Exception as e:
            st.error(f"Error al convertir el archivo: {str(e)}")

# Actualizar la función document_converter para incluir estas opciones
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
