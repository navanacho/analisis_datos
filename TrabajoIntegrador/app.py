# DASHBOARD INTERACTIVO - TPI ANÁLISIS DE DESEMPEÑO ACADÉMICO
# Hito 4: Interfaz Gráfica
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar página
st.set_page_config(
    page_title="Dashboard Académico",
    page_icon="🎓",
    layout="wide"
)

# CARGA DE DATOS (Con caché para optimización)
@st.cache_data
def cargar_datos():
    """Carga el dataset procesado del Hito 2"""
    df = pd.read_csv('StudentPerformanceFactors_procesado.csv')
    return df

df = cargar_datos()

# HEADER Y TÍTULO
st.title("Dashboard de Análisis de Desempeño Académico")
st.markdown("""
Este dashboard interactivo permite explorar los factores que influyen en el 
rendimiento académico de los estudiantes. **Filtre los datos** y observe cómo 
cambian las métricas en tiempo real.
""")
st.divider()

# BARRA LATERAL - FILTROS INTERACTIVOS

# Filtro por Tipo de Escuela
school_filter = st.sidebar.multiselect(
    "Tipo de Escuela:",
    options=df['School_Type'].unique(),
    default=df['School_Type'].unique()
)

# Filtro por Género
gender_filter = st.sidebar.multiselect(
    "Género:",
    options=df['Gender'].unique(),
    default=df['Gender'].unique()
)

# Filtro por Nivel de Ingresos
income_filter = st.sidebar.multiselect(
    "Nivel de Ingresos Familiares:",
    options=df['Family_Income'].unique(),
    default=df['Family_Income'].unique()
)

# Filtro por Rango de Notas
score_range = st.sidebar.slider(
    "Rango de Puntaje del Examen:",
    min_value=int(df['Exam_Score'].min()),
    max_value=int(df['Exam_Score'].max()),
    value=(int(df['Exam_Score'].min()), int(df['Exam_Score'].max()))
)

# Aplicar filtros
df_filtered = df[
    (df['School_Type'].isin(school_filter)) &
    (df['Gender'].isin(gender_filter)) &
    (df['Family_Income'].isin(income_filter)) &
    (df['Exam_Score'] >= score_range[0]) &
    (df['Exam_Score'] <= score_range[1])
]

# MÉTRICAS PRINCIPALES (KPIs)
st.subheader("Métricas Principales")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total de Estudiantes",
        value=len(df_filtered),
        delta=f"{len(df_filtered)/len(df)*100:.1f}% del total"
    )

with col2:
    st.metric(
        label="Promedio General",
        value=f"{df_filtered['Exam_Score'].mean():.1f}",
        delta=f"{df_filtered['Exam_Score'].mean() - df['Exam_Score'].mean():.1f}"
    )
    
with col3:
    st.metric(
        label="Nota Máxima",
        value=int(df_filtered['Exam_Score'].max()),
        delta="Puntaje más alto"
    )

with col4:
    st.metric(
        label="Nota Mínima",
        value=int(df_filtered['Exam_Score'].min()),
        delta="Puntaje más bajo"
    )

st.divider()

# PREGUNTA 1 ¿De qué manera el nivel de ingresos familiares condiciona la tasa de retorno de las tutorías académicas?
st.subheader("Pregunta 1: Ingresos Familiares vs Retorno de Tutorías")

col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df_filtered, x='Family_Income', y='Exam_Score', 
                hue='Tutoring_Sessions', ax=ax1, palette='Blues')
    ax1.set_title('Rendimiento por Ingresos y Tutorías', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)

with col2:
    st.markdown("""
    **Análisis:**
    - Los estudiantes con ingresos **High** tienden a tener mejores puntajes
    - El efecto de las tutorías es más visible en niveles de ingresos **Low** y **Medium**
    - **Recomendación:** Priorizar programas de tutoría para estudiantes de bajos ingresos
    """)

st.divider()
# PREGUNTA 2 ¿En qué medida un nivel alto de involucramiento parental puede neutralizar el impacto negativo de una "Calidad Docente" baja o media, y es este efecto más determinante en escuelas públicas que en privadas?
st.subheader("Pregunta 2: Involucramiento Parental y Calidad Docente")

col1, col2 = st.columns(2)

with col1:
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df_filtered, x='School_Type', y='Exam_Score', 
                hue='Parental_Involvement', ax=ax2, palette='viridis')
    ax2.set_title('Rendimiento por Escuela e Involucramiento', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)

with col2:
    st.markdown("""
    **Análisis:**
    - El involucramiento parental **High** mejora notas en TODOS los contextos
    - El efecto es MÁS FUERTE en escuelas públicas con calidad docente baja
    - **Recomendación:** Programas de participación familiar en escuelas públicas
    """)

st.divider()
# PREGUNTA 3 ¿En qué punto el incremento de horas de estudio comienza a mostrar rendimientos decrecientes debido a la privación de sueño o falta de actividad física?
st.subheader("Pregunta 3: Horas de Estudio y Rendimientos Decrecientes")

col1, col2 = st.columns(2)

with col1:
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_filtered, x='Hours_Studied', y='Exam_Score', 
                    hue='Sleep_Hours', size='Sleep_Hours', 
                    palette='coolwarm', sizes=(50, 200), alpha=0.6, ax=ax3)
    ax3.axvline(x=20, color='red', linestyle='--', linewidth=2, 
                label='Punto de inflexión (~20hs)')
    ax3.set_title('Horas de Estudio vs Rendimiento (con Sueño)', fontsize=12)
    ax3.legend()
    st.pyplot(fig3)

with col2:
    st.markdown("""
    **Análisis:**
    - El rendimiento CRECE hasta ~**15-20 horas** semanales de estudio
    - Después de 20 horas, la curva se ESTANCA o DISMINUYE
    - Estudiantes con **<6 horas de sueño** tienen peor rendimiento
    - **Recomendación:** Promover equilibrio estudio-descanso
    """)

st.divider()

# TABLA DE DATOS FILTRADOS
st.subheader("Datos Filtrados")

if st.checkbox("Mostrar tabla completa de datos filtrados"):
    st.dataframe(df_filtered, use_container_width=True)
    
    # Botón de descarga
    csv = df_filtered.to_csv(index=False, encoding='utf-8')
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name='datos_filtrados.csv',
        mime='text/csv'
    )
    
# FOOTER
st.divider()
st.markdown("""
**Dashboard desarrollado para el TPI de Análisis de Datos**  
*Los datos presentados son simulados con fines académicos*
""")