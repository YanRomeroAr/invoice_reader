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
        self.form_recognizer_endpoint = FORM_RECOGNIZER_ENDPOINT.rstrip('/')
        self.form_recognizer_key = FORM_RECOGNIZER_KEY
        self.computer_vision_endpoint = COMPUTER_VISION_ENDPOINT.rstrip('/')
        self.computer_vision_key = COMPUTER_VISION_KEY
    
    def analyze_with_form_recognizer(self, image_bytes):
        """Analizar documento con Form Recognizer - SIMPLIFICADO"""
        try:
            url = f"{self.form_recognizer_endpoint}/formrecognizer/documentModels/prebuilt-invoice:analyze?api-version=2023-07-31"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.form_recognizer_key,
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.post(url, headers=headers, data=image_bytes)
            
            if response.status_code == 202:
                operation_url = response.headers.get('Operation-Location')
                return self._wait_for_result(operation_url, self.form_recognizer_key)
            else:
                st.error(f"Form Recognizer Error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None
    
    def analyze_with_computer_vision(self, image_bytes):
        """Analizar con Computer Vision OCR - SIMPLIFICADO"""
        try:
            url = f"{self.computer_vision_endpoint}/vision/v3.2/read/analyze"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.computer_vision_key,
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.post(url, headers=headers, data=image_bytes)
            
            if response.status_code == 202:
                operation_url = response.headers.get('Operation-Location')
                return self._wait_for_result(operation_url, self.computer_vision_key)
            else:
                st.error(f"Computer Vision Error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None
    
    def _wait_for_result(self, operation_url, api_key):
        """Esperar resultado - SIMPLIFICADO"""
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        
        for i in range(20):  # Máximo 20 intentos
            try:
                response = requests.get(operation_url, headers=headers)
                result = response.json()
                
                status = result.get('status', '')
                
                if status == 'succeeded':
                    return result
                elif status == 'failed':
                    st.error("Análisis falló")
                    return None
                
                time.sleep(1)  # Esperar 1 segundo
                
            except:
                time.sleep(1)
                continue
        
        st.error("Timeout en análisis")
        return None
    
    def extract_data(self, form_result, ocr_result):
        """Extraer datos - SIMPLIFICADO"""
        data = {
            'document_type': 'Documento',
            'ruc': '',
            'business_name': '',
            'invoice_number': '',
            'total': '',
            'date': ''
        }
        
        # Obtener texto completo del OCR
        full_text = ""
        if ocr_result and 'analyzeResult' in ocr_result:
            pages = ocr_result['analyzeResult'].get('readResults', [])
            for page in pages:
                for line in page.get('lines', []):
                    full_text += line.get('text', '') + " "
        
        # Detectar tipo de documento
        text_upper = full_text.upper()
        if 'BOLETA' in text_upper:
            data['document_type'] = 'Boleta de Venta'
        elif 'FACTURA' in text_upper:
            data['document_type'] = 'Factura'
        
        # Extraer RUC
        ruc_match = re.search(r'RUC[:\s]*(\d{11})', full_text, re.IGNORECASE)
        if ruc_match:
            data['ruc'] = ruc_match.group(1)
        
        # Extraer número de documento
        doc_match = re.search(r'(\w\d{2}-\d{8})', full_text)
        if doc_match:
            data['invoice_number'] = doc_match.group(1)
        
        # Extraer datos estructurados de Form Recognizer
        if form_result and 'analyzeResult' in form_result:
            docs = form_result['analyzeResult'].get('documents', [])
            if docs:
                fields = docs[0].get('fields', {})
                
                if 'VendorName' in fields and 'content' in fields['VendorName']:
                    data['business_name'] = fields['VendorName']['content']
                
                if 'InvoiceTotal' in fields and 'content' in fields['InvoiceTotal']:
                    data['total'] = fields['InvoiceTotal']['content']
                
                if 'InvoiceDate' in fields and 'content' in fields['InvoiceDate']:
                    data['date'] = fields['InvoiceDate']['content']
        
        return data

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
        type=['png', 'jpg', 'jpeg'],
        help="Solo imágenes JPG o PNG (sin PDF por ahora)",
        label_visibility="collapsed"
    )
    
    if not uploaded_file:
        st.markdown("""
        <div style="text-align: center; color: #7f8c8d;">
            <h3>📱 Sube tu documento</h3>
            <p>Arrastra una imagen o haz clic para seleccionar</p>
            <small>Solo JPG, PNG • Máx. 4MB</small>
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
            
            # Leer archivo directamente
            file_bytes = uploaded_file.read()
            
            # Validar tamaño
            if len(file_bytes) > 4 * 1024 * 1024:
                st.error("❌ Archivo muy grande. Máximo 4MB.")
                return
            
            st.success(f"✅ Archivo listo: {len(file_bytes)} bytes")
            
            with st.spinner("🤖 Analizando..."):
                # Procesar con ambos servicios
                form_result = reader.analyze_with_form_recognizer(file_bytes)
                ocr_result = reader.analyze_with_computer_vision(file_bytes)
                
                if form_result or ocr_result:
                    # Extraer datos
                    invoice_data = reader.extract_data(form_result, ocr_result)
                    
                    # Mostrar resultados
                    st.markdown('<div class="success-badge">✅ Análisis completado</div>', 
                              unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="document-type">{invoice_data["document_type"]}</div>', 
                              unsafe_allow_html=True)
                    
                    # Métricas principales
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
                            <div class="metric-label">N° Doc</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Detalles
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    
                    if invoice_data['business_name']:
                        st.subheader("🏢 Empresa")
                        st.write(f"**{invoice_data['business_name']}**")
                    
                    if invoice_data['date']:
                        st.subheader("📅 Fecha")
                        st.write(invoice_data['date'])
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Ver datos técnicos
                    with st.expander("🔍 Ver datos técnicos"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Form Recognizer")
                            if form_result:
                                st.json(form_result)
                            else:
                                st.info("Sin datos")
                        
                        with col2:
                            st.subheader("Computer Vision")
                            if ocr_result:
                                st.json(ocr_result)
                            else:
                                st.info("Sin datos")
                
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
