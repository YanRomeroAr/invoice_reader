import streamlit as st
import requests
import json
import time
import base64
from PIL import Image
import io
import pandas as pd
from datetime import datetime
import re

# Configuración ultra minimalista
st.set_page_config(
    page_title="AI Invoice Reader • Perú",
    page_icon="🇵🇪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS moderno y minimalista
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .upload-zone {
        border: 2px dashed #e0e0e0;
        border-radius: 15px;
        padding: 3rem 2rem;
        text-align: center;
        background: #fafafa;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }
    
    .result-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 300;
        text-align: center;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    
    .success-badge {
        background: #27ae60;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .document-type {
        background: #3498db;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Configuración Azure
FORM_RECOGNIZER_ENDPOINT = st.secrets.get("FORM_RECOGNIZER_ENDPOINT", "")
FORM_RECOGNIZER_KEY = st.secrets.get("FORM_RECOGNIZER_KEY", "")
COMPUTER_VISION_ENDPOINT = st.secrets.get("COMPUTER_VISION_ENDPOINT", "")
COMPUTER_VISION_KEY = st.secrets.get("COMPUTER_VISION_KEY", "")

class PeruInvoiceReader:
    def __init__(self):
        self.form_recognizer_endpoint = FORM_RECOGNIZER_ENDPOINT
        self.form_recognizer_key = FORM_RECOGNIZER_KEY
        self.computer_vision_endpoint = COMPUTER_VISION_ENDPOINT
        self.computer_vision_key = COMPUTER_VISION_KEY
        """Preparar y validar datos de imagen"""
        try:
            # Leer archivo
            file_bytes = uploaded_file.read()
            
            # Validar tamaño (máximo 4MB para Azure)
            if len(file_bytes) > 4 * 1024 * 1024:
                st.error("❌ Archivo muy grande. Máximo 4MB permitido.")
                return None
            
            # Si es PDF, solo usar primeros bytes
            if uploaded_file.type == "application/pdf":
                return file_bytes
            
            # Si es imagen, convertir a formato compatible
            if uploaded_file.type.startswith('image'):
                try:
                    # Abrir imagen con PIL
                    image = Image.open(io.BytesIO(file_bytes))
                    
                    # Convertir a RGB si es necesario
                    if image.mode in ('RGBA', 'P', 'L'):
                        image = image.convert('RGB')
                    
                    # Redimensionar si es muy grande
                    max_size = (1920, 1920)
                    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                        image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Convertir a JPEG de calidad alta
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='JPEG', quality=95, optimize=True)
                    return img_byte_arr.getvalue()
                    
                except Exception as e:
                    st.error(f"❌ Error procesando imagen: {str(e)}")
                    return None
            
            return file_bytes
            
        except Exception as e:
            st.error(f"❌ Error preparando archivo: {str(e)}")
            return None
    def __init__(self):
        self.form_recognizer_endpoint = FORM_RECOGNIZER_ENDPOINT
        self.form_recognizer_key = FORM_RECOGNIZER_KEY
        self.computer_vision_endpoint = COMPUTER_VISION_ENDPOINT
        self.computer_vision_key = COMPUTER_VISION_KEY
    
    def analyze_with_form_recognizer(self, image_data):
        """Analizar documento con Form Recognizer"""
        try:
            # Asegurar que el endpoint termine con /
            endpoint = self.form_recognizer_endpoint.rstrip('/') + '/'
            analyze_url = f"{endpoint}formrecognizer/documentModels/prebuilt-invoice:analyze"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.form_recognizer_key,
                'Content-Type': 'application/octet-stream'
            }
            
            params = {'api-version': '2023-07-31'}
            
            response = requests.post(
                analyze_url,
                headers=headers,
                data=image_data,
                params=params,
                timeout=30
            )
            
            st.info(f"Form Recognizer Status: {response.status_code}")
            
            if response.status_code == 202:
                operation_location = response.headers.get('Operation-Location')
                if operation_location:
                    return self._wait_for_results(operation_location, self.form_recognizer_key)
                else:
                    st.error("No se recibió Operation-Location")
                    return None
            else:
                st.error(f"Error Form Recognizer: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error Form Recognizer: {str(e)}")
            return None
    
    def analyze_with_computer_vision(self, image_data):
        """Extraer texto con Computer Vision OCR"""
        try:
            # Asegurar que el endpoint termine con /
            endpoint = self.computer_vision_endpoint.rstrip('/') + '/'
            ocr_url = f"{endpoint}vision/v3.2/read/analyze"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.computer_vision_key,
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.post(
                ocr_url, 
                headers=headers, 
                data=image_data,
                timeout=30
            )
            
            st.info(f"Computer Vision Status: {response.status_code}")
            
            if response.status_code == 202:
                operation_location = response.headers.get('Operation-Location')
                if operation_location:
                    return self._wait_for_results(operation_location, self.computer_vision_key)
                else:
                    st.error("No se recibió Operation-Location para Computer Vision")
                    return None
            else:
                st.error(f"Error Computer Vision: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error Computer Vision: {str(e)}")
            return None
    
    def _wait_for_results(self, operation_location, api_key):
        """Esperar resultados del análisis"""
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        
        # Mostrar progreso
        progress_bar = st.progress(0)
        
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                progress = (attempt + 1) / max_attempts
                progress_bar.progress(progress)
                
                response = requests.get(operation_location, headers=headers, timeout=10)
                result = response.json()
                
                status = result.get('status', 'unknown')
                st.info(f"Estado: {status} (intento {attempt + 1}/{max_attempts})")
                
                if status == 'succeeded':
                    progress_bar.progress(1.0)
                    st.success("✅ Análisis completado")
                    return result
                elif status == 'failed':
                    st.error(f"❌ Análisis falló: {result.get('error', 'Error desconocido')}")
                    return None
                elif status in ['running', 'notStarted']:
                    time.sleep(2)
                else:
                    st.warning(f"Estado desconocido: {status}")
                    time.sleep(2)
                    
            except Exception as e:
                st.error(f"Error esperando resultados: {str(e)}")
                time.sleep(2)
        
        progress_bar.progress(1.0)
        st.error("⏱️ Timeout: El análisis tomó demasiado tiempo")
        return None
    
    def extract_peru_invoice_data(self, form_result, ocr_result):
        """Extraer datos específicos para documentos peruanos"""
        data = {
            'document_type': self._detect_document_type(ocr_result),
            'ruc': '',
            'business_name': '',
            'address': '',
            'invoice_number': '',
            'issue_date': '',
            'client_info': '',
            'subtotal': '',
            'igv': '',
            'total': '',
            'items': []
        }
        
        # Extraer de Form Recognizer
        if form_result and 'analyzeResult' in form_result:
            documents = form_result['analyzeResult'].get('documents', [])
            if documents:
                fields = documents[0].get('fields', {})
                
                data['business_name'] = self._get_field_value(fields.get('VendorName'))
                data['address'] = self._get_field_value(fields.get('VendorAddress'))
                data['invoice_number'] = self._get_field_value(fields.get('InvoiceId'))
                data['issue_date'] = self._get_field_value(fields.get('InvoiceDate'))
                data['client_info'] = self._get_field_value(fields.get('CustomerName'))
                data['subtotal'] = self._get_field_value(fields.get('SubTotal'))
                data['igv'] = self._get_field_value(fields.get('TotalTax'))
                data['total'] = self._get_field_value(fields.get('InvoiceTotal'))
        
        # Extraer RUC del texto OCR
        if ocr_result:
            full_text = self._extract_full_text(ocr_result)
            data['ruc'] = self._extract_ruc(full_text)
            
            # Si no encontró algunos datos en Form Recognizer, intentar con regex
            if not data['invoice_number']:
                data['invoice_number'] = self._extract_invoice_number(full_text)
        
        return data
    
    def _detect_document_type(self, ocr_result):
        """Detectar si es boleta o factura"""
        if not ocr_result:
            return "Documento"
            
        text = self._extract_full_text(ocr_result).upper()
        
        if 'BOLETA' in text:
            return "Boleta de Venta"
        elif 'FACTURA' in text:
            return "Factura"
        else:
            return "Documento Tributario"
    
    def _extract_ruc(self, text):
        """Extraer RUC del texto"""
        ruc_pattern = r'RUC[:\s]*(\d{11})'
        match = re.search(ruc_pattern, text, re.IGNORECASE)
        return match.group(1) if match else ''
    
    def _extract_invoice_number(self, text):
        """Extraer número de documento"""
        patterns = [
            r'(?:FACTURA|BOLETA)[^\d]*(\w\d{2}-\d{8})',
            r'(?:N°|NUM|#)[:\s]*(\w\d{2}-\d{8})',
            r'(\w\d{2}-\d{8})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ''
    
    def _extract_full_text(self, ocr_result):
        """Extraer texto completo del OCR"""
        text = ""
        if ocr_result and 'analyzeResult' in ocr_result:
            read_results = ocr_result['analyzeResult'].get('readResults', [])
            for page in read_results:
                for line in page.get('lines', []):
                    text += line.get('text', '') + " "
        return text
    
    def _get_field_value(self, field):
        """Obtener valor de campo"""
        return field.get('content', '') if field else ''

def main():
    # Header minimalista
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="header-title">🇵🇪 AI Invoice Reader</div>
    <div class="header-subtitle">Analiza boletas y facturas peruanas con inteligencia artificial</div>
    """, unsafe_allow_html=True)
    
    # Verificar credenciales
    if not all([FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY, 
                COMPUTER_VISION_ENDPOINT, COMPUTER_VISION_KEY]):
        st.error("🔑 Configura las credenciales de Azure en Streamlit Secrets")
        st.stop()
    
    reader = PeruInvoiceReader()
    
    # Zona de upload minimalista
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="Sube una imagen de tu boleta o factura (JPG, PNG recomendados)",
        label_visibility="collapsed"
    )
    
    if not uploaded_file:
        st.markdown("""
        <div style="text-align: center; color: #7f8c8d;">
            <h3>📱 Sube tu documento</h3>
            <p>Arrastra una imagen o haz clic para seleccionar</p>
            <small>Formatos: PNG, JPG, JPEG, PDF • Máx. 10MB</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file:
        # Mostrar imagen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            image = Image.open(uploaded_file)
            st.image(image, caption="", use_container_width=True)
        
        # Botón de análisis
        if st.button("🚀 Analizar Documento"):
            # Preparar datos de imagen
            image_data = reader.prepare_image_data(uploaded_file)
            
            if image_data is None:
                st.error("❌ No se pudo procesar el archivo")
                return
            
            st.success(f"✅ Archivo procesado: {len(image_data)} bytes")
            
            with st.spinner("🤖 Analizando con Azure AI..."):
                # Procesar con ambos servicios
                form_result = reader.analyze_with_form_recognizer(image_data)
                ocr_result = reader.analyze_with_computer_vision(image_data)
                
                if form_result or ocr_result:
                    # Extraer datos
                    invoice_data = reader.extract_peru_invoice_data(form_result, ocr_result)
                    
                    # Badge de éxito
                    st.markdown('<div class="success-badge">✅ Análisis completado</div>', 
                              unsafe_allow_html=True)
                    
                    # Tipo de documento
                    st.markdown(f'<div class="document-type">{invoice_data["document_type"]}</div>', 
                              unsafe_allow_html=True)
                    
                    # Resultados en cards
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    
                    # Información principal en métricas
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{invoice_data['total'] or 'N/A'}</div>
                            <div class="metric-label">Total</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{invoice_data['ruc'] or 'N/A'}</div>
                            <div class="metric-label">RUC</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{invoice_data['invoice_number'] or 'N/A'}</div>
                            <div class="metric-label">N° Documento</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Detalles en formato limpio
                    if invoice_data['business_name']:
                        st.subheader("🏢 Emisor")
                        st.write(f"**{invoice_data['business_name']}**")
                        if invoice_data['address']:
                            st.caption(invoice_data['address'])
                    
                    if invoice_data['client_info']:
                        st.subheader("👤 Cliente")
                        st.write(invoice_data['client_info'])
                    
                    if invoice_data['issue_date']:
                        st.subheader("📅 Fecha")
                        st.write(invoice_data['issue_date'])
                    
                    # Totales si están disponibles
                    if any([invoice_data['subtotal'], invoice_data['igv']]):
                        st.subheader("💰 Desglose")
                        if invoice_data['subtotal']:
                            st.write(f"Subtotal: **{invoice_data['subtotal']}**")
                        if invoice_data['igv']:
                            st.write(f"IGV: **{invoice_data['igv']}**")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Expandir para ver datos técnicos
                    with st.expander("🔍 Ver datos técnicos"):
                        tab1, tab2 = st.tabs(["Form Recognizer", "Computer Vision"])
                        
                        with tab1:
                            if form_result:
                                st.json(form_result)
                            else:
                                st.info("No hay datos de Form Recognizer")
                        
                        with tab2:
                            if ocr_result:
                                full_text = reader._extract_full_text(ocr_result)
                                st.text_area("Texto extraído:", full_text, height=200)
                            else:
                                st.info("No hay datos de Computer Vision")
                
                else:
                    st.error("❌ No se pudo procesar el documento")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer minimalista
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
        Powered by <strong>Azure Form Recognizer</strong> + <strong>Computer Vision</strong><br>
        Especializado para documentos tributarios del Perú 🇵🇪
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
