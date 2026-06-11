import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Dashboard Logística", page_icon="🚚", layout="wide")

# 2. TÍTULO Y DESCRIPCIÓN
st.title("🚚 Centro de Monitoreo - Logística Cuyo")
st.markdown("Dashboard interactivo en tiempo real conectado a nuestro motor PostgreSQL.")
st.divider() # Dibuja una línea separadora

# 3. FUNCIÓN DE CONEXIÓN A LA BASE DE DATOS
# Usamos el decorador @st.cache_data para no saturar a PostgreSQL con consultas repetidas
@st.cache_data
def cargar_datos():
    engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/logistica_cuyo_db")
    query = "SELECT * FROM envios"
    # Leemos la query y la convertimos en DataFrame
    df = pd.read_sql_query(query, con=engine)
    return df

# Ejecutamos la función y guardamos los datos
df_envios = cargar_datos()

# 4. BARRA LATERAL (FILTROS)
st.sidebar.header("Filtros Operativos")
# Creamos un menú desplegable leyendo los barrios únicos de nuestro DataFrame
barrio_seleccionado = st.sidebar.selectbox(
    "Seleccione un Barrio:", 
    options=["Todos"] + list(df_envios['barrio'].unique())
)

# Aplicamos el filtro al DataFrame original
if barrio_seleccionado != "Todos":
    df_filtrado = df_envios[df_envios['barrio'] == barrio_seleccionado]
else:
    df_filtrado = df_envios

# 5. CÁLCULO DE KPIs (Usando los datos filtrados)
recaudacion_total = df_filtrado['valor_ars'].sum()
cantidad_pedidos = df_filtrado['id_pedido'].count()

# 6. DIBUJANDO LA INTERFAZ
# Creamos dos columnas para poner los KPIs lado a lado
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Recaudación Total", value=f"${recaudacion_total:,.2f}")

with col2:
    st.metric(label="Volumen de Pedidos", value=cantidad_pedidos)

st.markdown("### 📋 Detalle de Operaciones")
# Mostramos el DataFrame resultante
st.dataframe(df_filtrado, use_container_width=True)

# 7. GRÁFICO RÁPIDO INTEGRADO
st.markdown("### 📊 Tendencia de Recaudación")
# Agrupamos los datos y los graficamos en una línea
datos_grafico = df_filtrado.groupby('Fecha_Envio')['valor_ars'].sum()
st.line_chart(datos_grafico)