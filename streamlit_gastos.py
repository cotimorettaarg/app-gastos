
import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Autenticación con Google Sheets usando secrets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_key = json.loads(st.secrets["gcp_service_account"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
client = gspread.authorize(credentials)

# --- Conexión a la hoja de cálculo ---
SHEET_NAME = "Gastos Compartidos"
sheet = client.open(SHEET_NAME).sheet1

# --- Interfaz Streamlit ---
st.title("💰 Registro de Gastos Compartidos")

# Formulario de ingreso
with st.form("registro_gastos"):
    persona = st.selectbox("¿Quién hizo el gasto?", ["Constanza", "Matías"])
    monto = st.number_input("Monto del gasto", min_value=0.0, format="%.2f")
    metodo = st.selectbox("Método de pago", ["Efectivo", "Tarjeta", "Mercado Pago"])
    categoria = st.selectbox("Categoría", [
        "Comida", "Amigos", "Regalo", "Regalo Mío", "Vitto", "Tenis", "Pádel", "Viaje",
        "Indumentaria", "Zapatillas", "River", "Pilates", "Yoga", "Uber/Didi", "Gimnasio"
    ])
    enviar = st.form_submit_button("Guardar gasto")

# Enviar datos a Google Sheets
if enviar:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fila = [fecha, persona, monto, metodo, categoria]
    try:
        sheet.append_row(fila)
        st.success("✅ Gasto guardado en Google Sheets.")
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")
