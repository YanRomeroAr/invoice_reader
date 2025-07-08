import streamlit as st
import requests
import time
from PIL import Image
import io
import re

# Configuración
st.set_page_config(
    page_title="Trabajo IA Computer Vision",
    page_icon="🤖",
    layout="centered"
)

# CSS super limpio - fondo blanco y texto oscuro
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
        color: #2c2c2c;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    .header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 2px solid #e8e8e8;
        margin-bottom: 2rem;
    }
    
    .title {
        font-size: 2.8rem;
        color: #1a1a1a;
        margin-bottom: 0.3rem;
        font-weight: 600;
    }
    
    .subtitle {
        color: #4a4a4a;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .project-title {
        color: #666666;
        font-size: 0.95rem;
        font-style: italic;
        margin-bottom: 1rem;
    }
    
    .result-box {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        background-color: #fafafa;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .metric {
        background-color: #f5f5f5;
        border: 1px solid #dadada;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .metric-value {
        font-size: 1.4rem;
        font-weight: bold;
        color: #1a1a1a;
        margin-bottom: 0.3rem;
    }
    
    .metric-label {
        color: #666666;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .success {
        background-color: #e8f5e8;
        color: #2d5016;
        padding: 0.8rem 1.2rem;
        border-radius: 6px;
        border: 1px solid #c3e6c3;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .error {
        background-color: #fde8e8;
        color: #721c24;
        padding: 0.8rem 1.2rem;
        border-radius: 6px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .info-section {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 0 6px 6px 0;
    }
    
    .footer {
        text-align: center;
        color: #555555;
        padding: 2rem 1rem;
        border-top: 1px solid #e8e8e8;
        margin-top: 3rem;
        background-color: #fafafa;
    }
    
    .creator {
        font-weight: 600;
        color: #333333;
        font-size: 1.1rem;
    }
    
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,123,255,0.2);
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,123,255,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Credenciales Azure
FORM_RECOGNIZER_ENDPOINT = st.secrets.get("FORM_RECOGNIZER_ENDPOINT", "")
FORM_RECOGNIZER_KEY = st.secrets.get("FORM_RECOGNIZER_KEY", "")
COMPUTER_VISION_ENDPOINT = st.secrets.get("COMPUTER_VISION_ENDPOINT", "")
COMPUTER_VISION_KEY = st.secrets.get("COMPUTER_VISION_KEY", "")

class InvoiceReader:
    def __init__(self):
        self.form_endpoint = FORM_RECOGNIZER_ENDPOINT.rstrip('/')
        self.form_key = FORM_RECOGNIZER_KEY
        self.vision_endpoint = COMPUTER_VISION_ENDPOINT.rstrip('/')
        self.vision_key = COMPUTER_VISION_KEY
    
    def analyze_with_form_recognizer(self, image_bytes):
        """Analizar con Form Recognizer"""
        try:
            url = f"{self.form_endpoint}/formrecognizer/documentModels/prebuilt-invoice:analyze?api-version=2023-07-31"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.form_key,
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.post(url, headers=headers, data=image_bytes, timeout=30)
            
            if response.status_code == 202:
                operation_url = response.headers.get('Operation-Location')
                return self._wait_for_result(operation_url, self.form_key)
            else:
                st.error(f"Error Form Recognizer: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None
    
    def analyze_with_computer_vision(self, image_bytes):
        """Analizar con Computer Vision"""
        try:
            url = f"{self.vision_endpoint}/vision/v3.2/read/analyze"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.vision_key,
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.post(url, headers=headers, data=image_bytes, timeout=30)
            
            if response.status_code == 202:
                operation_url = response.headers.get('Operation-Location')
                return self._wait_for_result(operation_url, self.vision_key)
            else:
                st.error(f"Error Computer Vision: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None
    
    def _wait_for_result(self, operation_url, api_key):
        """Esperar resultado"""
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        
        progress = st.progress(0)
        status_text = st.empty()
        
        for i in range(30):
            try:
                response = requests.get(operation_url, headers=headers, timeout=10)
                result = response.json()
                
                status = result.get('status', '')
                progress.progress((i + 1) / 30)
                status_text.text(f"Procesando... {status}")
                
                if status == 'succeeded':
                    progress.progress(1.0)
                    status_text.text("✅ Completado")
                    return result
                elif status == 'failed':
                    st.error("❌ Procesamiento falló")
                    return None
                
                time.sleep(1)
                
            except Exception as e:
                time.sleep(1)
                continue
        
        st.error("⏱️ Tiempo agotado")
        return None
    
    def extract_data(self, form_result, ocr_result):
        """Extraer datos importantes"""
        data = {
            'tipo_documento': 'Documento',
            'ruc': '',
            'razon_social': '',
            'numero_documento': '',
            'fecha': '',
            'total': '',
            'subtotal': '',
            'igv': ''
        }
        
        # Extraer texto completo del OCR
        full_text = ""
        if ocr_result and 'analyzeResult' in ocr_result:
            pages = ocr_result['analyzeResult'].get('readResults', [])
            for page in pages:
                for line in page.get('lines', []):
                    full_text += line.get('text', '') + " "
        
        # Detectar tipo de documento
        text_upper = full_text.upper()
        if 'BOLETA' in text_upper:
            data['tipo_documento'] = 'Boleta de Venta'
        elif 'FACTURA' in text_upper:
            data['tipo_documento'] = 'Factura'
        
        # Extraer RUC (formato peruano: 11 dígitos)
        ruc_pattern = r'RUC[:\s]*(\d{11})'
        ruc_match = re.search(ruc_pattern, full_text, re.IGNORECASE)
        if ruc_match:
            data['ruc'] = ruc_match.group(1)
        
        # Extraer número de documento (formato: F001-00000001)
        doc_patterns = [
            r'(\w\d{2,3}-\d{6,8})',
            r'(?:N°|NUM)[:\s]*(\w\d{2,3}-\d{6,8})'
        ]
        for pattern in doc_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                data['numero_documento'] = match.group(1)
                break
        
        # Extraer datos estructurados de Form Recognizer
        if form_result and 'analyzeResult' in form_result:
            docs = form_result['analyzeResult'].get('documents', [])
            if docs and 'fields' in docs[0]:
                fields = docs[0]['fields']
                
                # Mapear campos
                field_mapping = {
                    'VendorName': 'razon_social',
                    'InvoiceDate': 'fecha',
                    'InvoiceTotal': 'total',
                    'SubTotal': 'subtotal',
                    'TotalTax': 'igv'
                }
                
                for azure_field, data_key in field_mapping.items():
                    if azure_field in fields and 'content' in fields[azure_field]:
                        data[data_key] = fields[azure_field]['content']
        
        return data

def main():
    # Header
    st.markdown("""
    <div class="header">
        <div class="project-title">Trabajo IA Computer Vision</div>
        <div class="title">🤖 Lector de Facturas Perú</div>
        <div class="subtitle">Sistema de extracción de datos usando Azure AI</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar credenciales
    if not all([FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY, 
                COMPUTER_VISION_ENDPOINT, COMPUTER_VISION_KEY]):
        st.error("⚠️ Faltan credenciales de Azure. Configura los secrets.")
        st.stop()
    
    # Inicializar lector
    reader = InvoiceReader()
    
    # Upload de archivo
    st.markdown("### 📄 Subir Documento")
    uploaded_file = st.file_uploader(
        "Selecciona una imagen de tu boleta o factura",
        type=['png', 'jpg', 'jpeg'],
        help="Formatos soportados: PNG, JPG, JPEG"
    )
    
    if uploaded_file:
        # Mostrar imagen
        image = Image.open(uploaded_file)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Documento cargado")
        
        # Información del archivo
        file_size = len(uploaded_file.read())
        uploaded_file.seek(0)  # Reset
        
        st.info(f"📊 Archivo: {uploaded_file.name} ({file_size:,} bytes)")
        
        # Botón de análisis
        if st.button("🚀 Analizar Documento", type="primary"):
            
            if file_size > 4 * 1024 * 1024:  # 4MB
                st.error("❌ Archivo muy grande. Máximo 4MB permitido.")
                return
            
            # Leer archivo
            file_bytes = uploaded_file.read()
            
            with st.spinner("Analizando documento..."):
                
                # Procesar con ambos servicios
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🔍 Form Recognizer**")
                    form_result = reader.analyze_with_form_recognizer(file_bytes)
                
                with col2:
                    st.markdown("**👁️ Computer Vision**")
                    ocr_result = reader.analyze_with_computer_vision(file_bytes)
                
                # Verificar si al menos uno funcionó
                if form_result or ocr_result:
                    
                    # Extraer datos
                    data = reader.extract_data(form_result, ocr_result)
                    
                    # Mostrar resultados
                    st.markdown("---")
                    st.markdown("### 📋 Resultados")
                    
                    # Tipo de documento
                    st.markdown(f"**Tipo:** {data['tipo_documento']}")
                    
                    # Métricas principales en columnas
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric">
                            <div class="metric-value">{data['total'] or 'N/A'}</div>
                            <div class="metric-label">Total</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric">
                            <div class="metric-value">{data['ruc'] or 'N/A'}</div>
                            <div class="metric-label">RUC</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric">
                            <div class="metric-value">{data['numero_documento'] or 'N/A'}</div>
                            <div class="metric-label">N° Documento</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Detalles adicionales
                    st.markdown("### 📊 Detalles")
                    
                    details_col1, details_col2 = st.columns(2)
                    
                    with details_col1:
                        if data['razon_social']:
                            st.markdown(f"**Razón Social:** {data['razon_social']}")
                        if data['fecha']:
                            st.markdown(f"**Fecha:** {data['fecha']}")
                    
                    with details_col2:
                        if data['subtotal']:
                            st.markdown(f"**Subtotal:** {data['subtotal']}")
                        if data['igv']:
                            st.markdown(f"**IGV:** {data['igv']}")
                    
                    # Datos técnicos (expandible)
                    with st.expander("🔍 Ver datos técnicos"):
                        
                        tab1, tab2 = st.tabs(["Form Recognizer", "Computer Vision"])
                        
                        with tab1:
                            if form_result:
                                st.json(form_result)
                            else:
                                st.info("No hay datos de Form Recognizer")
                        
                        with tab2:
                            if ocr_result:
                                st.json(ocr_result)
                            else:
                                st.info("No hay datos de Computer Vision")
                
                else:
                    st.error("❌ No se pudo procesar el documento. Verifica que sea una imagen clara.")
    
    else:
        # Instrucciones cuando no hay archivo
        st.markdown("""
        ### 📋 Instrucciones
        
        1. **Sube una imagen** de tu boleta o factura peruana
        2. **Formatos aceptados:** JPG, PNG  
        3. **Tamaño máximo:** 4MB
        4. **Calidad recomendada:** Imagen clara y legible
        
        El sistema extraerá automáticamente:
        - RUC del emisor
        - Número de documento  
        - Totales e impuestos
        - Fecha de emisión
        - Razón social
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; padding: 1rem;">
        Powered by <strong>Azure Form Recognizer</strong> + <strong>Computer Vision</strong><br>
        Especializado para documentos tributarios del Perú 🇵🇪
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
