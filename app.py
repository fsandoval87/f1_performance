import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="Dashboard de Desempeño de F1",
    page_icon="🏎️",
    layout="wide",
)

# Estilo visual general para Seaborn
sns.set_theme(style="whitegrid")


@st.cache_data
def cargar_datos(ruta_archivo):
    """Carga el archivo CSV manejando posibles excepciones."""
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(
            f"No se encontró el archivo en la ruta: {ruta_archivo}")
    return pd.read_csv(ruta_archivo)


# --- TÍTULO Y SUBTÍTULO ---
st.title("🏎️ Dashboard de Desempeño de Escuderías de Fórmula 1")
st.markdown(
    "### Análisis interactivo de las últimas temporadas y rendimiento en"
    " pista"
)
st.markdown("---")

# --- CARGA DE DATOS CON MANEJO DE EXCEPCIONES ---
ruta_csv = "data/data.csv"

try:
    df = cargar_datos(ruta_csv)
except FileNotFoundError as e:
    st.error(
        "⚠️ **Error crítico:** No se pudo encontrar el archivo de datos"
        f" requerido (`{ruta_csv}`)."
    )
    st.info(
        "Por favor, asegúrate de colocar el archivo CSV dentro de la carpeta"
        " `data/` con el nombre `data.csv`."
    )
    st.stop()
except Exception as e:
    st.error(f"⚠️ Ocurrió un error inesperado al cargar los datos: {e}")
    st.stop()

# --- SECCIÓN: VISTA PREVIA DE DATOS (CHECKBOX) ---
if st.checkbox("Mostrar las primeras 5 filas del conjunto de datos"):
    st.subheader("Vista previa de los datos")
    st.dataframe(df.head(), use_container_width=True)
    st.markdown("---")

# --- FILTROS INTERACTIVOS (SIDEBAR) ---
st.sidebar.header("🔍 Panel de Filtros")

# Filtro por escudería (Dropdown múltiple o único)
escuderias_disponibles = sorted(df["escuderia"].unique())
escuderias_seleccionadas = st.sidebar.multiselect(
    "Selecciona Escudería(s):",
    options=escuderias_disponibles,
    default=escuderias_disponibles,
)

# Filtro por Clima (Dropdown)
climas_disponibles = ["Todos"] + sorted(df["clima"].unique().tolist())
clima_seleccionado = st.sidebar.selectbox("Clima:", options=climas_disponibles)

# Aplicar filtros al DataFrame
df_filtrado = df[df["escuderia"].isin(escuderias_seleccionadas)]
if clima_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["clima"] == clima_seleccionado]

# Validar si el filtro quedó vacío
if df_filtrado.empty:
    st.warning(
        "⚠️ No hay datos disponibles para los filtros seleccionados. Intenta"
        " ajustar tus criterios."
    )
    st.stop()

# --- SECCIÓN DE GRÁFICOS (TRES COLUMNAS) ---
st.subheader("📊 Análisis Visual de Rendimiento")
col1, col2, col3 = st.columns(3)

# 1. Gráfico de barras: Proporción de podios por escudería
with col1:
    st.markdown("#### Proporción de Podios")
    fig, ax = plt.subplots(figsize=(6, 4))

    # Calculamos la suma de podios (True/False) o conteo de podios True por escudería
    podios_df = (
        df_filtrado.groupby("escuderia")["podio"].sum().reset_index()
    )

    sns.barplot(
        data=podios_df,
        x="escuderia",
        y="podio",
        palette="viridis",
        ax=ax,
        hue="escuderia",
        legend=False,
    )
    ax.set_title("Total de Podios por Escudería", fontsize=10)
    ax.set_xlabel("Escudería", fontsize=9)
    ax.set_ylabel("Número de Podios", fontsize=9)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)

# 2. Histograma: Distribución de DNF (Carreras no finalizadas)
with col2:
    st.markdown("#### Distribución de DNF")
    fig, ax = plt.subplots(figsize=(6, 4))

    # Convertimos DNF booleano a entero para contar
    df_filtrado_dnf = df_filtrado.copy()
    df_filtrado_dnf["dnf_int"] = df_filtrado_dnf["dnf"].astype(int)

    sns.histplot(
        data=df_filtrado_dnf[df_filtrado_dnf["dnf_int"] == 1],
        x="escuderia",
        discrete=True,
        color="crimson",
        ax=ax,
    )
    ax.set_title("Frecuencia de Retiros (DNF) por Escudería", fontsize=10)
    ax.set_xlabel("Escudería", fontsize=9)
    ax.set_ylabel("Cantidad de DNF", fontsize=9)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)

# 3. Scatterplot: Temperatura de pista vs Tiempo de carrera mínimo
with col3:
    st.markdown("#### Temperatura vs Tiempo")
    fig, ax = plt.subplots(figsize=(6, 4))

    sns.scatterplot(
        data=df_filtrado,
        x="temperatura_pista_c",
        y="tiempo_carrera_min",
        hue="escuderia",
        palette="deep",
        ax=ax,
        s=70,
    )
    ax.set_title("Temp. Pista vs Tiempo de Carrera", fontsize=10)
    ax.set_xlabel("Temp. Pista (°C)", fontsize=9)
    ax.set_ylabel("Tiempo Carrera (min)", fontsize=9)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=7)
    plt.tight_layout()
    st.pyplot(fig)

# Pie de página opcional
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Desarrollado con Streamlit &"
    " Seaborn 🚀</div>",
    unsafe_allow_html=True,
)
