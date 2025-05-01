
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import calendar

# --- Autenticación con Google Sheets usando secrets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_key = st.secrets["gcp_service_account"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
client = gspread.authorize(credentials)

# --- Conexión a la hoja de cálculo ---
SHEET_ID = "TU_SPREADSHEET_ID"  # Reemplazar si usás open_by_key
sheet = client.open("Gastos Compartidos").sheet1

# --- Seguridad: código de acceso ---
st.image("https://cdn-icons-png.flaticon.com/512/1946/1946436.png", width=100)
codigo = st.text_input("🔒 Ingresá el código para acceder a la app", type="password")

if codigo != "4982":
    st.warning("Código incorrecto o vacío. Ingresá el código para continuar.")
    st.stop()

# --- Interfaz principal ---
st.title("🏠 Registro de Gastos Compartidos")

with st.form("registro_gastos"):
    persona = st.selectbox("¿Quién hizo el gasto?", ["Constanza", "Matías"])
    monto = st.number_input("Monto total del gasto", min_value=0.0, format="%.2f")
    metodo = st.selectbox("Método de pago", ["Efectivo", "Tarjeta", "Mercado Pago"])
    categoria = st.selectbox("Categoría", [
        "Comida", "Amigos", "Regalo", "Regalo Mío", "Vitto", "Tenis", "Pádel",
        "Indumentaria", "Zapatillas", "River", "Pilates", "Yoga", "Uber/Didi", "Gimnasio",
        "Viaje", "viaje- aéreo", "viaje- ropa", "viaje-hotel", "viaje-transporte",
        "viaje-comida", "viaje-atracciones"
    ])

    cuotas = 1
    banco = "-"
    mes_inicio = datetime.now().month
    anio_inicio = datetime.now().year

    if metodo == "Tarjeta":
        banco = st.selectbox("Banco emisor", ["Galicia", "Santander", "Macro", "BBVA", "Otro"])
        cuotas = st.number_input("Cantidad de cuotas", min_value=1, step=1)
        mes_inicio = st.selectbox("Mes de inicio", list(calendar.month_name)[1:], index=datetime.now().month - 1)
        anio_inicio = st.number_input("Año de inicio", min_value=datetime.now().year, value=datetime.now().year)

    enviar = st.form_submit_button("Guardar gasto")

# --- Procesar envío ---
if enviar:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if metodo == "Tarjeta":
        mes_inicio_idx = list(calendar.month_name).index(mes_inicio)
        valor_cuota = round(monto / cuotas, 2)
        for i in range(int(cuotas)):
            mes = mes_inicio_idx + i
            anio = anio_inicio + (mes - 1) // 12
            mes_real = (mes - 1) % 12 + 1
            mes_nombre = calendar.month_name[mes_real]
            fila = [fecha, persona, valor_cuota, metodo, categoria, f"{i+1}/{int(cuotas)}", f"{mes_nombre} {anio}", banco]
            try:
                sheet.append_row(fila)
            except Exception as e:
                st.error(f"❌ Error al guardar cuota {i+1}: {e}")
        st.success("✅ Cuotas guardadas en Google Sheets.")
    else:
        mes_nombre_actual = calendar.month_name[datetime.now().month]
        anio_actual = datetime.now().year
        fila = [fecha, persona, monto, metodo, categoria, "-", f"{mes_nombre_actual} {anio_actual}", banco]
        try:
            sheet.append_row(fila)
            st.success("✅ Gasto guardado en Google Sheets.")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
