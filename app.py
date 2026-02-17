import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# 1. Configuración inicial
st.set_page_config(page_title="Asistente Experto HCl", page_icon="🧪")
st.title("🧪 Asistente Experto: Gestión Ambiental y Riesgos")

# --- PANEL DE DIAGNÓSTICO PARA EL USUARIO ---
st.sidebar.header("⚙️ Panel de Diagnóstico")

archivos_esperados = [
    "Matriz_Ambiental_Corregida_Seccion_1.csv",
    "Matriz_Ambiental_Corregida_Seccion_2.csv",
    "Matriz_What_If_Corregida_Seccion_2.csv"
]

archivos_ok = True
for arch in archivos_esperados:
    if os.path.exists(arch):
        st.sidebar.success(f"✅ Archivo leído: {arch}")
    else:
        st.sidebar.error(f"❌ Falta el archivo: {arch}")
        archivos_ok = False

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-pro')
    st.sidebar.success("✅ Motor Gemini conectado.")
except Exception as e:
    st.sidebar.error("❌ Falla en la API Key.")

# Si faltan archivos, detenemos la planta (la app) aquí mismo
if not archivos_ok:
    st.warning("⚠️ ALARMA DE SISTEMA: No se encuentran los archivos CSV. Verifica en GitHub que los nombres sean EXACTAMENTE iguales a los listados en el panel izquierdo.")
    st.stop()

# ----------------------------------------------

# 2. Cargar datos (Solo se ejecuta si los archivos existen)
@st.cache_data
def cargar_matrices():
    m1 = pd.read_csv("Matriz_Ambiental_Corregida_Seccion_1.csv")
    m2 = pd.read_csv("Matriz_Ambiental_Corregida_Seccion_2.csv")
    m3 = pd.read_csv("Matriz_What_If_Corregida_Seccion_2.csv")
    # Convertimos a texto limitando el tamaño para evitar saturar la memoria de la API
    return f"Matriz 1:\n{m1.to_string()}\n\nMatriz 2:\n{m2.to_string()}\n\nWhat-If:\n{m3.to_string()}"

contexto_matrices = cargar_matrices()

# 3. Interfaz del Chat
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    st.chat_message(msg["role"]).write(msg["contenido"])

if pregunta := st.chat_input("Ej: ¿Qué norma aplica si falla la válvula del tanque B-110?"):
    st.session_state.mensajes.append({"role": "user", "contenido": pregunta})
    st.chat_message("user").write(pregunta)

    prompt_experto = f"""
    Eres un ingeniero ambiental experto en sistemas de gestión y normatividad mexicana (STPS, SEMARNAT).
    Responde brevemente basándote SOLO en esta información de las matrices del proceso de HCl:
    
    {contexto_matrices}
    
    Pregunta: {pregunta}
    """
    
    try:
        respuesta = model.generate_content(prompt_experto)
        st.session_state.mensajes.append({"role": "assistant", "contenido": respuesta.text})
        st.chat_message("assistant").write(respuesta.text)
    except Exception as e:
        st.error(f"Error de comunicación con Gemini: {e}")
