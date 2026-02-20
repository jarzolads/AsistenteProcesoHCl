import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# 1. Configuración de la página (Layout ancho para mejor distribución)
st.set_page_config(page_title="Experto Normativo HCl", page_icon="🏭", layout="wide")

# --- ESTILOS VISUALES (CSS básico para títulos) ---
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; color: #0056b3; font-weight: bold; text-align: center; }
    .sub-title { font-size: 1.1rem; color: #4F4F4F; text-align: center; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🏭 Asistente Experto: Gestión Ambiental y Riesgos</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Auditoría Normativa - Tren de Producción de Ácido Clorhídrico</p>', unsafe_allow_html=True)
st.divider()

# --- PANEL LATERAL (DIAGNÓSTICO) ---
with st.sidebar:
    st.header("⚙️ Estado de la Planta (Sistema)")
    
    archivos_esperados = [
        "Matriz_Ambiental_Corregida_Seccion_1.csv",
        "Matriz_Ambiental_Corregida_Seccion_2.csv",
        "Matriz_What_If_Corregida_Seccion_2.csv"
    ]

    archivos_ok = True
    for arch in archivos_esperados:
        if os.path.exists(arch):
            st.success(f"✅ Documento listo: {arch}")
        else:
            st.error(f"❌ Falta el archivo: {arch}")
            archivos_ok = False

    st.divider()
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Se sugiere gemini-1.5-flash para mayor velocidad en el chat
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.success("✅ Conexión con Gemini establecida.")
    except Exception as e:
        st.error("❌ Falla en la llave de acceso (API Key).")
        
    st.divider()
    st.info("💡 **Tip de auditoría:** Pide que te desglose el índice de un Análisis de Riesgos para un equipo en específico.")

if not archivos_ok:
    st.warning("⚠️ ALARMA: Faltan archivos de las matrices. Verifica en GitHub.")
    st.stop()

# --- ÁREA PRINCIPAL: DOS COLUMNAS ---
# La columna izquierda (col1) será un poco más grande que la derecha (col2)
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📊 Diagrama de Tubería e Instrumentación (DTI)")
    
    # Intentar cargar la imagen del DTI
    nombre_imagen = "DTI Proceso HCl Sección 1.jpg"
    if os.path.exists(nombre_imagen):
        st.image(nombre_imagen, caption="DTI - Sección 1", use_container_width=True)
    else:
        st.info("📌 La imagen del DTI no se encontró. Asegúrate de subir 'DTI Proceso HCl Sección 1.jpg' a GitHub.")
        
    with st.expander("👁️ Inspeccionar Datos de Matrices"):
        st.write("El asistente está leyendo estos datos en tiempo real:")
        st.dataframe(pd.read_csv("Matriz_What_If_Corregida_Seccion_2.csv").head(3)) # Muestra una vista previa bonita

with col2:
    st.subheader("💬 Asistente Consultivo")
    
    @st.cache_data
    def cargar_matrices():
        m1 = pd.read_csv("Matriz_Ambiental_Corregida_Seccion_1.csv")
        m2 = pd.read_csv("Matriz_Ambiental_Corregida_Seccion_2.csv")
        m3 = pd.read_csv("Matriz_What_If_Corregida_Seccion_2.csv")
        return f"Matriz 1:\n{m1.to_string()}\n\nMatriz 2:\n{m2.to_string()}\n\nWhat-If:\n{m3.to_string()}"

    contexto_matrices = cargar_matrices()

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    # Contenedor con altura fija para que el chat no empuje la página hacia abajo
    chat_container = st.container(height=500)
    
    with chat_container:
        for msg in st.session_state.mensajes:
            st.chat_message(msg["role"]).write(msg["contenido"])

    if pregunta := st.chat_input("Ej: Genera la estructura del Análisis de Riesgos (NOM-028) para el B-110"):
        st.session_state.mensajes.append({"role": "user", "contenido": pregunta})
        with chat_container:
            st.chat_message("user").write(pregunta)

            prompt_experto = f"""
            Eres un auditor experto en sistemas de gestión (ISO 14001/45001) y normatividad mexicana (STPS, SEMARNAT, CONAGUA).
            
            Tienes acceso a las siguientes matrices del proceso de producción de HCl:
            {contexto_matrices}
            
            Pregunta del usuario: {pregunta}
            
            INSTRUCCIONES OBLIGATORIAS:
            1. Base de datos: Analiza el equipo usando estrictamente la información de las matrices provistas.
            2. Precisión Normativa: Al mencionar la legislación, DEBES indicar los APARTADOS, CAPÍTULOS O ARTÍCULOS específicos de la norma.
            3. Estructura Documental: Si el requerimiento legal implica un documento (Análisis de Riesgos, Plan de Emergencias, etc.), GENERA UNA ESTRUCTURA SUGERIDA detallada (índice, capítulos) para el ingeniero.
            4. Formato: Presenta la información de forma ejecutiva con formato Markdown.
            """
            
            try:
                respuesta = model.generate_content(prompt_experto)
                st.session_state.mensajes.append({"role": "assistant", "contenido": respuesta.text})
                st.chat_message("assistant").write(respuesta.text)
            except Exception as e:
                st.error(f"Error de comunicación con Gemini: {e}")
