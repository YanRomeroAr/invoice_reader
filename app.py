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

# CSS super limpio - fondo blanco y TODAS las letras negras
st.markdown("""
<style>
    /* Forzar todos los textos a negro */
    * {
        color: #000000 !important;
    }
    
    .main {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Todos los elementos de texto */
    .stMarkdown, .stMarkdown *, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        background-color: transparent !important;
    }
    
    /* Elementos específicos de Streamlit */
    .stSelectbox label, .stFileUploader label, .stButton, .stProgress {
        color: #000000 !important;
    }
    
    /* Texto en inputs y labels */
    label, .stTextInput label, .stFileUploader label {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 2px solid #e8e8e8;
        margin-bottom: 2rem;
        background-color: #ffffff !important;
    }
    
    .title {
        font-size: 2.8rem;
        color: #000000 !important;
        margin-bottom: 0.3rem;
        font-weight: 700;
    }
    
    .subtitle {
        color: #000000 !important;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .project-title {
        color: #000000 !important;
        font-size: 0.95rem;
        font-style: italic;
        margin-bottom: 1rem;
        font-weight: 600;
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
        color: #000000 !important;
        margin-bottom: 0.3rem;
    }
    
    .metric-label {
        color: #000000 !important;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .success {
        background-color: #e8f5e8;
        color: #000000 !important;
        padding: 0.8rem 1.2rem;
        border-radius: 6px;
        border: 1px solid #c3e6c3;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .error {
        background-color: #fde8e8;
        color: #000000 !important;
        padding: 0.8rem 1.2rem;
        border-radius: 6px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .info-section {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 0 6px 6px 0;
    }
    
    .info-section * {
        color: #000000 !important;
    }
    
    .footer {
        text-align: center;
        color: #000000 !important;
        padding: 2rem 1rem;
        border-top: 1px solid #e8e8e8;
        margin-top: 3rem;
        background-color: #fafafa;
    }
    
    .creator {
        font-weight: 700;
        color: #000000 !important;
        font-size: 1.1rem;
    }
    
    .stButton > button {
        background-color: #007bff;
        color: #ffffff !important;
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
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,123,255,0.3);
    }
    
    /* Progress bars y otros elementos */
    .stProgress .stProgress-bar {
        background-color: #007bff !important;
    }
    
    /* Spinners y loading */
    .stSpinner {
        color: #000000 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* JSON viewer */
    .stJson {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* Info, success, error messages */
    .stAlert {
        color: #000000 !important;
    }
    
    /* Cualquier texto que se escape */
    .css-1v0mbdj, .css-1ekf893, .css-16huue1, .css-1d391kg {
        color: #000000 !important;
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
        <div class="info-section">
            <h3>📋 Instrucciones de Uso</h3>
            
            <p><strong>1. Sube una imagen</strong> de tu boleta o factura peruana</p>
            <p><strong>2. Formatos aceptados:</strong> JPG, PNG</p>
            <p><strong>3. Tamaño máximo:</strong> 4MB</p>
            <p><strong>4. Calidad recomendada:</strong> Imagen clara y legible</p>
            
            <h4>🎯 El sistema extraerá automáticamente:</h4>
            <ul>
                <li>RUC del emisor</li>
                <li>Número de documento</li>
                <li>Totales e impuestos (IGV)</li>
                <li>Fecha de emisión</li>
                <li>Razón social</li>
                <li>Tipo de documento (Boleta/Factura)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="margin-bottom: 1rem;">
            <strong>Tecnologías utilizadas:</strong><br>
            Azure Form Recognizer • Azure Computer Vision • Streamlit • Python
        </div>
        <div style="margin-bottom: 0.5rem;">
            Especializado para documentos tributarios del Perú 🇵🇪
        </div>
        <div class="creator">
            Creado por Yan Romero
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
