
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import calendar
import uuid

# --- Autenticación con Google Sheets usando secrets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_key = st.secrets["gcp_service_account"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
client = gspread.authorize(credentials)

# --- Conexión a la hoja de cálculo ---
sheet = client.open("Gastos Compartidos").sheet1

# --- Seguridad: código de acceso ---
st.image("https://cdn-icons-png.flaticon.com/512/1946/1946436.png", width=100)
codigo = st.text_input("🔒 Ingresá el código para acceder a la app", type="password")

if codigo != "4982":
    st.warning("Código incorrecto o vacío. Ingresá el código para continuar.")
    st.stop()

# --- Interfaz principal ---
st.title("🏠 Registro de Gastos Compartidos")

# Campos del formulario
persona = st.selectbox("¿Quién hizo el gasto?", ["Constanza", "Matías"])
monto = st.number_input("Monto total del gasto", min_value=0.0, format="%.2f")
metodo = st.selectbox("Método de pago", ["Efectivo", "Tarjeta", "Mercado Pago"])
categoria = st.selectbox("Categoría", [
    "Comida", "Cena", "Almuerzo", "Merienda", "Desayuno", "Amigos", "Salida",
    "Regalo", "Regalo Mío", "Vitto", "Tenis", "Pádel", "Indumentaria", "Zapatillas", "River",
    "Pilates", "Yoga", "Uber/Didi", "Gimnasio", "Viaje", "viaje- aéreo", "viaje- ropa",
    "viaje-hotel", "viaje-transporte", "viaje-comida", "viaje-atracciones", "Combustible",
    "Educación", "Artículo limpieza", "Casa- mueble", "Casa-perfumería", "Casa-arreglo",
    "Herramienta trabajo", "Service auto", "Otro"
])

concepto_otro = ""
if categoria == "Otro":
    concepto_otro = st.text_input("Ingresá el concepto del gasto")

# Campos adicionales si es tarjeta
cuotas = 1
banco = "-"
mes_inicio = datetime.now().month
anio_inicio = datetime.now().year

if metodo == "Tarjeta":
    banco = st.selectbox("Banco emisor", ["GGAL MATI", "GGAL PATRI", "GGAL MYR", "BBVA", "YOY", "BNA"])
    cuotas = st.number_input("Cantidad de cuotas", min_value=1, step=1, value=1)
    mes_inicio = st.selectbox("Mes de inicio", list(calendar.month_name)[1:], index=datetime.now().month - 1)
    anio_inicio = st.number_input("Año de inicio", min_value=datetime.now().year, value=datetime.now().year)

# Botón de envío
enviar = st.button("Guardar gasto")

# --- Procesar envío ---
if enviar:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gasto_id = str(uuid.uuid4())[:8]
    categoria_final = concepto_otro if categoria == "Otro" and concepto_otro else categoria

    if metodo == "Tarjeta":
        mes_inicio_idx = list(calendar.month_name).index(mes_inicio)
        valor_cuota = round(monto / cuotas, 2)
        filas = []
        for i in range(int(cuotas)):
            mes = mes_inicio_idx + i
            anio = anio_inicio + (mes - 1) // 12
            mes_real = (mes - 1) % 12 + 1
            mes_nombre = calendar.month_name[mes_real]
            fila = [gasto_id, fecha, persona, valor_cuota, metodo, categoria_final, f"{i+1}/{int(cuotas)}", f"{mes_nombre} {anio}", banco]
            filas.append(fila)
        try:
            sheet.append_rows(filas)
            st.success(f"✅ Cuotas guardadas en Google Sheets con ID: `{gasto_id}`")
        except Exception as e:
            st.error(f"❌ Error al guardar cuotas: {e}")
    else:
        mes_nombre_actual = calendar.month_name[datetime.now().month]
        anio_actual = datetime.now().year
        fila = [gasto_id, fecha, persona, monto, metodo, categoria_final, "-", f"{mes_nombre_actual} {anio_actual}", banco]
        try:
            sheet.append_row(fila)
            st.success(f"✅ Gasto guardado en Google Sheets con ID: `{gasto_id}`")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
