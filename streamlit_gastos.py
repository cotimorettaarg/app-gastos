
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dateutil.relativedelta import relativedelta

# --- Logo y título ---
col1, col2 = st.columns([1, 10])
with col1:
    st.image("https://raw.githubusercontent.com/cotimorettaarg/app-gastos/main/logo.png", width=60)
with col2:
    st.markdown("## Seguimiento de Gastos Compartidos")

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
    gastos = pd.DataFrame(columns=["Fecha", "Usuario", "Importe", "Método", "Categoría", "Tarjeta"])

# --- Registro de gasto ---
st.sidebar.header("📝 Registrar nuevo gasto")

usuario = st.sidebar.selectbox("Usuario", ["Matías", "Constanza"])
importe = st.sidebar.number_input("Importe del gasto ($)", min_value=0.0, step=10.0)
metodo = st.sidebar.selectbox("Método de pago", ["Efectivo", "Tarjeta", "Mercado Pago"])
categoria = st.sidebar.selectbox("Categoría", [
    "Comida", "Amigos", "Regalo", "Regalo mío", "Vitto", "Tenis",
    "Pádel", "Viaje", "Alquiler", "Servicios", "Limpieza", "Educación",
    "Psicólogo", "Indumentaria", "Zapatillas", "River", "Pilates", "Yoga", "Uber/DiDi", "Gimnasio"
])

cuotas = 1
mes_inicio = None
tarjeta = ""

if metodo == "Tarjeta":
    tarjeta = st.sidebar.selectbox("Tarjeta utilizada", ["GGAL-MO", "GGAL-PE", "GGAL-PA", "YOY", "BNA", "BBVA"])
    cuotas = st.sidebar.number_input("Cantidad de cuotas", min_value=1, step=1, value=1)
    hoy = datetime.today()
    meses_opciones = [(hoy + relativedelta(months=i)).strftime("%Y-%m") for i in range(60)]
    mes_inicio = st.sidebar.selectbox("Mes en que comienza a pagarse:", meses_opciones)

if st.sidebar.button("💾 Guardar gasto"):
    hoy = datetime.today()
    if metodo == "Tarjeta" and cuotas > 1 and mes_inicio:
        fecha_inicio = datetime.strptime(mes_inicio + "-01", "%Y-%m-%d")
        cuota_valor = round(importe / cuotas, 2)
        for i in range(cuotas):
            fecha_cuota = (fecha_inicio + relativedelta(months=i)).strftime("%Y-%m-%d")
            nueva_fila = {
                "Fecha": fecha_cuota,
                "Usuario": usuario,
                "Importe": cuota_valor,
                "Método": metodo,
                "Categoría": categoria,
                "Tarjeta": tarjeta
            }
            gastos = pd.concat([gastos, pd.DataFrame([nueva_fila])], ignore_index=True)
        st.success("✅ Cuotas registradas correctamente.")
    else:
        fecha_final = fecha_inicio.strftime('%Y-%m-%d') if metodo == "Tarjeta" and mes_inicio else hoy.strftime('%Y-%m-%d')
        nueva_fila = {
            "Fecha": fecha_final,
            "Usuario": usuario,
            "Importe": importe,
            "Método": metodo,
            "Categoría": categoria,
            "Tarjeta": tarjeta if metodo == "Tarjeta" else ""
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
        st.success("✅ Gasto guardado correctamente.")

    gastos.to_csv(ARCHIVO, index=False)
    st.rerun()

# --- Eliminar gasto específico ---
st.subheader("🗑️ Eliminar un gasto")
if not gastos.empty:
    gastos["ID"] = gastos.index
    gasto_seleccionado = st.selectbox("Seleccioná un gasto para eliminar", gastos[["ID", "Fecha", "Usuario", "Importe", "Categoría"]].astype(str).apply(lambda row: " | ".join(row), axis=1).tolist())
    if st.button("Eliminar gasto seleccionado"):
        index_a_borrar = int(gasto_seleccionado.split(" | ")[0])
        gastos.drop(index=index_a_borrar, inplace=True)
        gastos.to_csv(ARCHIVO, index=False)
        st.success("✅ Gasto eliminado correctamente.")
        st.rerun()
else:
    st.info("No hay gastos cargados para eliminar.")

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



# --- Cuotas activas por mes ---
if not gastos.empty:
    st.subheader("📅 Cuotas activas por mes (solo tarjeta)")
    df_cuotas = gastos[gastos["Método"] == "Tarjeta"].copy()
    if not df_cuotas.empty:
        df_cuotas["Mes"] = df_cuotas["Fecha"].str[:7]
        resumen = df_cuotas.groupby("Mes").agg(
            Cuotas_activas=("Importe", "count"),
            Total_cuotas= ("Importe", "sum")
        ).reset_index()

        st.dataframe(resumen)

        st.bar_chart(resumen.set_index("Mes")["Total_cuotas"])
    else:
        st.info("No hay cuotas activas registradas aún.")
