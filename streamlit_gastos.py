
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Mostrar logo desde GitHub ---
col1, col2 = st.columns([1, 10])
with col1:
    st.image("https://raw.githubusercontent.com/cotimorettaarg/app-gastos/main/logo.png", width=60)
with col2:
    st.title("App de Gastos Compartidos")

# --- PIN de acceso ---
pin = st.text_input("Ingresá el PIN para continuar", type="password")
if pin != "4982":
    st.warning("🔒 Ingresá el PIN correcto para acceder.")
    st.stop()

# Archivo CSV
ARCHIVO = "gastos_streamlit.csv"
if os.path.exists(ARCHIVO):
    gastos = pd.read_csv(ARCHIVO)
else:
    gastos = pd.DataFrame(columns=["Fecha", "Usuario", "Importe", "Método", "Categoría"])

# --- Registro de gasto ---
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

# --- Dashboard y eliminación ---
st.subheader("📋 Últimos gastos")
if not gastos.empty:
    gastos["id"] = gastos.index
    gasto_a_eliminar = st.selectbox("Seleccioná un gasto para eliminar (ID)", gastos["id"].tolist())
    if st.button("🗑️ Eliminar gasto seleccionado"):
        gastos = gastos[gastos["id"] != gasto_a_eliminar]
        gastos.drop(columns="id", inplace=True)
        gastos.to_csv(ARCHIVO, index=False)
        st.success("✅ Gasto eliminado.")
        st.experimental_rerun()
else:
    st.info("No hay gastos cargados todavía.")

# --- Estadísticas y gráficos ---
if not gastos.empty:
    with st.expander("🔍 Filtros"):
        filtro_usuario = st.selectbox("Filtrar por usuario", ["Todos"] + sorted(gastos["Usuario"].unique()))
        filtro_mes = st.selectbox("Filtrar por mes", sorted(gastos["Fecha"].str[:7].unique()))

    df_filtrado = gastos.copy()
    if filtro_usuario != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Usuario"] == filtro_usuario]
    df_filtrado = df_filtrado[df_filtrado["Fecha"].str.startswith(filtro_mes)]

    st.subheader("📈 Evolución de gastos")
    st.dataframe(df_filtrado.sort_values("Fecha", ascending=False))

    st.metric("💰 Total", f"${df_filtrado['Importe'].sum():,.2f}")

    st.bar_chart(df_filtrado.groupby("Categoría")["Importe"].sum())
    st.line_chart(df_filtrado.groupby("Fecha")["Importe"].sum())
