
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- PIN de acceso ---
st.title("🔐 Acceso a la App de Gastos")
pin = st.text_input("Ingresá el PIN para continuar", type="password")

if pin != "4982":
    st.warning("🔒 Ingresá el PIN correcto para acceder.")
    st.stop()

# Archivo CSV donde se guardan los datos
ARCHIVO = "gastos_streamlit.csv"

# Cargar datos si existe, si no crear uno nuevo
if os.path.exists(ARCHIVO):
    gastos = pd.read_csv(ARCHIVO)
else:
    gastos = pd.DataFrame(columns=["Fecha", "Usuario", "Importe", "Método", "Categoría"])

# --- Sidebar: Registro de gasto ---
st.sidebar.header("📝 Registrar nuevo gasto")

with st.sidebar.form("form_gasto"):
    usuario = st.selectbox("Usuario", ["Matías", "Constanza"])
    importe = st.number_input("Importe del gasto ($)", min_value=0.0, step=10.0)
    metodo = st.selectbox("Método de pago", ["Efectivo", "Tarjeta", "Mercado Pago"])
    categoria = st.selectbox("Categoría", [
        "Comida", "Amigos", "Regalo", "Regalo mío", "Vitto", "Tenis",
        "Pádel", "Viaje", "Alquiler", "Servicios", "Limpieza", "Educación", "Psicólogo"
    ])
    submit = st.form_submit_button("💾 Guardar")

    if submit and importe > 0:
        nueva_fila = {
            "Fecha": datetime.today().strftime('%Y-%m-%d'),
            "Usuario": usuario,
            "Importe": importe,
            "Método": metodo,
            "Categoría": categoria
        }

        # Verificar duplicado
        duplicado = (
            (gastos["Fecha"] == nueva_fila["Fecha"]) &
            (gastos["Usuario"] == nueva_fila["Usuario"]) &
            (gastos["Importe"] == nueva_fila["Importe"]) &
            (gastos["Método"] == nueva_fila["Método"]) &
            (gastos["Categoría"] == nueva_fila["Categoría"])
        )
        if duplicado.any():
            st.warning("⚠️ Este gasto ya fue registrado hoy. Si querés cargarlo igual, cambiá alguno de los campos.")
            st.stop()

        gastos = pd.concat([gastos, pd.DataFrame([nueva_fila])], ignore_index=True)
        gastos.to_csv(ARCHIVO, index=False)
        st.success("✅ Gasto guardado correctamente.")

# --- Main: Dashboard ---
st.title("📊 Seguimiento de Gastos Compartidos")

if gastos.empty:
    st.info("No hay gastos cargados todavía.")
else:
    # Filtros
    with st.expander("🔍 Filtros"):
        filtro_usuario = st.selectbox("Filtrar por usuario", ["Todos"] + sorted(gastos["Usuario"].unique()))
        filtro_mes = st.selectbox("Filtrar por mes", sorted(gastos["Fecha"].str[:7].unique()))

    df_filtrado = gastos.copy()
    if filtro_usuario != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Usuario"] == filtro_usuario]
    df_filtrado = df_filtrado[df_filtrado["Fecha"].str.startswith(filtro_mes)]

    # Mostrar tabla
    st.subheader("📋 Últimos gastos")
    st.dataframe(df_filtrado.sort_values("Fecha", ascending=False).reset_index(drop=True))

    # Estadísticas
    st.subheader("💰 Totales")
    total = df_filtrado["Importe"].sum()
    st.metric(label="Total filtrado", value=f"${total:,.2f}")

    # Categorías
    st.subheader("📌 Gastos por categoría")
    resumen_categoria = df_filtrado.groupby("Categoría")["Importe"].sum()
    st.bar_chart(resumen_categoria)

    # Evolución diaria
    st.subheader("📈 Evolución diaria")
    diario = df_filtrado.groupby("Fecha")["Importe"].sum()
    st.line_chart(diario)
