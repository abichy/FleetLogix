
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2

st.set_page_config(
    page_title="FleetLogix Dashboard",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 FleetLogix | Dashboard Logístico")
st.caption("Análisis interactivo de entregas — PostgreSQL")

@st.cache_data(ttl=300)
def cargar_datos():
    with psycopg2.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "fleetlogix"),
        user=os.getenv("PGUSER", "fleetlogix_user"),
        password=os.environ["PGPASSWORD"]
    ) as conn:
        return pd.read_sql_query(
            """
            SELECT delivery_status, scheduled_datetime
            FROM deliveries
            """,
            conn
        )

try:
    datos = cargar_datos()
except Exception as error:
    st.error("No se pudo conectar a PostgreSQL.")
    st.caption(f"Detalle técnico: {error}")
    st.stop()

datos["scheduled_datetime"] = pd.to_datetime(
    datos["scheduled_datetime"]
)

min_fecha = datos["scheduled_datetime"].min().date()
max_fecha = datos["scheduled_datetime"].max().date()

fechas = st.date_input(
    "Filtrar por fechas",
    value=(min_fecha, max_fecha),
    min_value=min_fecha,
    max_value=max_fecha
)

if len(fechas) == 2:
    inicio, fin = fechas
    datos = datos[
        datos["scheduled_datetime"].dt.date.between(inicio, fin)
    ]

total = len(datos)
entregadas = (datos["delivery_status"] == "delivered").sum()
pendientes = (datos["delivery_status"] == "pending").sum()
cumplimiento = (entregadas / total * 100) if total else 0

a, b, c, d = st.columns(4)
a.metric("Entregas totales", f"{total:,}")
b.metric("Entregadas", f"{entregadas:,}")
c.metric("Pendientes", f"{pendientes:,}")
d.metric("Cumplimiento", f"{cumplimiento:.2f}%")

izq, der = st.columns(2)

with izq:
    estados = (
        datos["delivery_status"]
        .value_counts()
        .reset_index()
    )
    estados.columns = ["Estado", "Cantidad"]

    fig = px.pie(
        estados,
        names="Estado",
        values="Cantidad",
        title="Distribución de entregas",
        hole=0.45
    )
    st.plotly_chart(fig, use_container_width=True)

with der:
    diario = (
        datos.groupby(
            datos["scheduled_datetime"].dt.date
        )
        .size()
        .reset_index(name="Cantidad")
    )
    diario.columns = ["Fecha", "Cantidad"]

    fig = px.line(
        diario,
        x="Fecha",
        y="Cantidad",
        title="Evolución diaria de entregas"
    )
    st.plotly_chart(fig, use_container_width=True)

st.success("Dashboard FleetLogix funcionando correctamente")
