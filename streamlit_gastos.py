
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
    gastos = pd.DataFrame(columns=["Fecha", "Usuario", "Importe", "Método", "Categoría"])

# --- Registro de gasto ---
st.sidebar.header("📝 Registrar nuevo gasto")
with st.sidebar.form("form_gasto"):
    usuario = st.selectbox("Usuario", ["Matías", "Constanza"])
    importe = st.number_input("Importe del gasto ($)", min_value=0.0, step=10.0)
    metodo = st.selectbox("Método de pago", ["Efectivo", "Tarjeta", "Mercado Pago"])
    categoria = st.selectbox("Categoría", [
        "Comida", "Amigos", "Regalo", "Regalo mío", "Vitto", "Tenis",
        "Pádel", "Viaje", "Alquiler", "Servicios", "Limpieza", "Educación",
        "Psicólogo", "Indumentaria", "Zapatillas", "River"
    ])

    cuotas = 1
    mes_inicio = None
    if metodo == "Tarjeta":
        cuotas = st.number_input("Cantidad de cuotas", min_value=1, step=1, value=1)
        mes_inicio = st.text_input("Mes de inicio (formato YYYY-MM):", value=datetime.today().strftime("%Y-%m"))

    submit = st.form_submit_button("💾 Guardar")

    if submit and importe > 0:
        hoy = datetime.today()
        if metodo == "Tarjeta" and cuotas > 1 and mes_inicio:
            try:
                fecha_inicio = datetime.strptime(mes_inicio + "-01", "%Y-%m-%d")
                cuota_valor = round(importe / cuotas, 2)
                for i in range(cuotas):
                    fecha_cuota = (fecha_inicio + relativedelta(months=i)).strftime("%Y-%m-%d")
                    nueva_fila = {
                        "Fecha": fecha_cuota,
                        "Usuario": usuario,
                        "Importe": cuota_valor,
                        "Método": metodo,
                        "Categoría": categoria
                    }
                    gastos = pd.concat([gastos, pd.DataFrame([nueva_fila])], ignore_index=True)
                st.success("✅ Cuotas registradas correctamente.")
            except:
                st.error("⚠️ Error en el formato del mes de inicio. Usá YYYY-MM.")
        else:
            nueva_fila = {
                "Fecha": hoy.strftime('%Y-%m-%d'),
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
            st.success("✅ Gasto guardado correctamente.")

        gastos.to_csv(ARCHIVO, index=False)
        st.experimental_rerun()

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
        st.experimental_rerun()
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
