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

# Estilo visual consistente para todos los gráficos
sns.set_theme(style="whitegrid")
PALETA = "viridis"

# Orden lógico para las variables ordinales (evita el orden arbitrario de .unique())
ORDEN_NIVEL = ['Low', 'Medium', 'High']

# CARGA DE DATOS (Con caché para optimización)
@st.cache_data
def cargar_datos():
    """Carga el dataset procesado del Hito 2"""
    df = pd.read_csv('StudentPerformanceFactors_procesado.csv')
    return df

df = cargar_datos()


def opciones_ordenadas(serie, orden=ORDEN_NIVEL):
    """Devuelve los valores únicos de una serie respetando un orden lógico."""
    presentes = list(serie.dropna().unique())
    ordenados = [v for v in orden if v in presentes]
    # Agrega cualquier valor que no esté en el orden definido al final
    return ordenados + [v for v in presentes if v not in orden]


# HEADER Y TÍTULO
st.title("🎓 Dashboard de Análisis de Desempeño Académico")
st.markdown("""
Este dashboard interactivo permite explorar los factores que influyen en el
rendimiento académico de los estudiantes. **Ajustá los filtros** de la barra lateral
y observá cómo cambian las métricas y los gráficos en tiempo real.
""")
st.divider()

# BARRA LATERAL - FILTROS INTERACTIVOS
st.sidebar.header("🔎 Filtros")
st.sidebar.caption("Por defecto se muestran todos los estudiantes. Deseleccioná opciones para acotar el análisis.")

# Filtro por Tipo de Escuela
school_filter = st.sidebar.multiselect(
    "Tipo de Escuela:",
    options=list(df['School_Type'].dropna().unique()),
    default=list(df['School_Type'].dropna().unique())
)

# Filtro por Género
gender_filter = st.sidebar.multiselect(
    "Género:",
    options=list(df['Gender'].dropna().unique()),
    default=list(df['Gender'].dropna().unique())
)

# Filtro por Nivel de Ingresos
income_options = opciones_ordenadas(df['Family_Income'])
income_filter = st.sidebar.multiselect(
    "Nivel de Ingresos Familiares:",
    options=income_options,
    default=income_options
)

# Filtro por Calidad Docente
teacher_options = opciones_ordenadas(df['Teacher_Quality'])
teacher_filter = st.sidebar.multiselect(
    "Calidad Docente:",
    options=teacher_options,
    default=teacher_options
)

# Filtro por Involucramiento Parental
involvement_options = opciones_ordenadas(df['Parental_Involvement'])
involvement_filter = st.sidebar.multiselect(
    "Involucramiento Parental:",
    options=involvement_options,
    default=involvement_options
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
    (df['Teacher_Quality'].isin(teacher_filter)) &
    (df['Parental_Involvement'].isin(involvement_filter)) &
    (df['Exam_Score'] >= score_range[0]) &
    (df['Exam_Score'] <= score_range[1])
]

# Contador en vivo de estudiantes filtrados
st.sidebar.divider()
st.sidebar.metric("Estudiantes filtrados", f"{len(df_filtered):,}".replace(",", "."))

# GUARDA: si no hay datos tras filtrar, detener antes de calcular métricas (evita crash)
if df_filtered.empty:
    st.warning("⚠️ No hay estudiantes que cumplan los filtros seleccionados. Ajustá los filtros de la barra lateral.")
    st.stop()

# MÉTRICAS PRINCIPALES (KPIs)
st.subheader("📌 Métricas Principales")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total de Estudiantes",
        value=f"{len(df_filtered):,}".replace(",", "."),
        delta=f"{len(df_filtered)/len(df)*100:.1f}% del total"
    )

with col2:
    st.metric(
        label="Promedio General",
        value=f"{df_filtered['Exam_Score'].mean():.1f}",
        delta=f"{df_filtered['Exam_Score'].mean() - df['Exam_Score'].mean():+.1f} vs. global"
    )

with col3:
    st.metric(
        label="Nota Máxima",
        value=int(df_filtered['Exam_Score'].max()),
        delta=f"Mediana: {df_filtered['Exam_Score'].median():.0f}"
    )

with col4:
    st.metric(
        label="Nota Mínima",
        value=int(df_filtered['Exam_Score'].min()),
        delta=f"Desvío: {df_filtered['Exam_Score'].std():.1f}"
    )

st.divider()

# PREGUNTA 1 ¿De qué manera el nivel de ingresos familiares condiciona la tasa de retorno de las tutorías académicas?
st.subheader("Pregunta 1: Ingresos Familiares vs Retorno de Tutorías")

col1, col2 = st.columns([3, 2])

with col1:
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.pointplot(
        data=df_filtered, x='Tutoring_Sessions', y='Exam_Score',
        hue='Family_Income', hue_order=income_options,
        palette=PALETA, ax=ax1, errorbar=None, marker='o'
    )
    ax1.set_title('Nota media según nº de tutorías, por nivel de ingresos', fontsize=12)
    ax1.set_xlabel('Sesiones de tutoría')
    ax1.set_ylabel('Nota media del examen')
    ax1.legend(title='Ingresos familiares')
    st.pyplot(fig1)
    st.caption("Cada línea muestra la nota media en función del número de tutorías para un nivel de ingresos.")

with col2:
    st.markdown("""
    **Análisis (según los datos):**
    - Las tutorías **mejoran la nota en TODOS los niveles de ingresos**, con una tendencia
      ascendente y sostenida (0 → 5 sesiones).
    - La ganancia es incluso **mayor en ingresos altos** (≈ **+2.9 pts**, de 66.8 a 69.6)
      que en ingresos bajos (≈ **+2.3 pts**) o medios (≈ **+2.1 pts**).
    - No se observa que las tutorías "nivelen" la brecha por ingresos: el orden de los
      niveles se mantiene en casi todo el rango.
    - **Recomendación:** ampliar el acceso a tutorías es positivo en general; para
      *reducir desigualdad* hay que combinarlas con apoyo dirigido a los hogares de menores ingresos.
    """)

st.divider()
# PREGUNTA 2 ¿En qué medida un nivel alto de involucramiento parental puede neutralizar el impacto negativo de una "Calidad Docente" baja o media, y es este efecto más determinante en escuelas públicas que en privadas?
st.subheader("Pregunta 2: ¿El Involucramiento Parental compensa una Calidad Docente baja?")

col1, col2 = st.columns([3, 2])

with col1:
    pivot = df_filtered.pivot_table(
        index='Teacher_Quality', columns='Parental_Involvement',
        values='Exam_Score', aggfunc='mean'
    )
    # Reordenar filas/columnas de forma lógica (solo las presentes tras filtrar)
    filas = [v for v in ORDEN_NIVEL if v in pivot.index]
    cols = [v for v in ORDEN_NIVEL if v in pivot.columns]
    pivot = pivot.reindex(index=filas, columns=cols)

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        pivot, annot=True, fmt='.1f', cmap='YlGnBu', ax=ax2,
        linewidths=0.5, cbar_kws={'label': 'Nota media del examen'}
    )
    ax2.set_title('Nota media: Calidad Docente vs Involucramiento Parental', fontsize=12)
    ax2.set_xlabel('Involucramiento Parental')
    ax2.set_ylabel('Calidad Docente')
    st.pyplot(fig2)
    st.caption("Cada celda es la nota media de la combinación. Más oscuro = mejor rendimiento.")

with col2:
    st.markdown("""
    **Análisis (según los datos):**
    - El **mejor resultado** se da con Docente *High* + Involucramiento *High* (**≈ 68.4**).
    - Con **Calidad Docente baja**, subir el involucramiento de *Low* a *High* recupera
      **≈ +1.4 pts** (65.9 → 67.3): **compensa parcialmente, no del todo** el déficit docente.
    - El **tipo de escuela es prácticamente irrelevante** (Pública 67.88 vs Privada 67.87):
      lo determinante es el involucramiento, no si la escuela es pública o privada.
    - **Recomendación:** los programas de participación familiar ayudan en cualquier contexto,
      pero **no reemplazan** la mejora de la calidad docente.
    """)

st.divider()
# PREGUNTA 3 ¿En qué punto el incremento de horas de estudio comienza a mostrar rendimientos decrecientes debido a la privación de sueño o falta de actividad física?
st.subheader("Pregunta 3: Horas de Estudio y Rendimiento")

col1, col2 = st.columns([3, 2])

with col1:
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    # Nube de puntos con color según horas de sueño
    sns.scatterplot(
        data=df_filtered, x='Hours_Studied', y='Exam_Score',
        hue='Sleep_Hours', palette='coolwarm', alpha=0.4, ax=ax3, legend='brief'
    )
    # Línea de tendencia real (regresión) para mostrar el crecimiento sostenido
    sns.regplot(
        data=df_filtered, x='Hours_Studied', y='Exam_Score',
        scatter=False, color='black', ax=ax3,
        line_kws={'linewidth': 2, 'label': 'Tendencia'}
    )
    ax3.set_title('Horas de estudio vs Rendimiento (color = horas de sueño)', fontsize=12)
    ax3.set_xlabel('Horas de estudio semanales')
    ax3.set_ylabel('Nota del examen')
    ax3.legend(title='Sueño / Tendencia', loc='upper left', fontsize=8)
    st.pyplot(fig3)
    st.caption("La línea negra es la tendencia real: el rendimiento crece de forma sostenida con las horas de estudio.")

with col2:
    st.markdown("""
    **Análisis (según los datos):**
    - El rendimiento **crece de forma sostenida** con las horas de estudio, **sin rendimientos
      decrecientes** en el rango observado (0–10 h: ≈63.7 → 30+ h: ≈70.9). Correlación **0.52**.
    - **El sueño NO muestra efecto** sobre la nota (correlación ≈ **0.0**): no se confirma que
      dormir poco perjudique el rendimiento en estos datos.
    - El factor **más correlacionado** con la nota es en realidad la **Asistencia** (corr **0.67**),
      por encima de las horas de estudio.
    - **Recomendación:** sostener la asistencia y el hábito de estudio; no hay evidencia de un
      "techo" a partir del cual estudiar más sea contraproducente.
    """)

st.divider()

# TABLA DE DATOS FILTRADOS
st.subheader("📄 Datos Filtrados")

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
