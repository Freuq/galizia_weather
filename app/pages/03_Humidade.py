import streamlit as st
import pandas as pd
import plotly.express as px
from utils.filters import *
from utils.df_functions import *
from utils.graphics import *

st.set_page_config(layout="wide", page_title="Morriña en Galicia - Humedad", page_icon="🌫️")
cargar_css("app/static/styles.css")

# Cargar tu dataframe (esto puedes adaptarlo si usas session_state o carga desde archivo)
# Cargar datos
if "df_climatico" not in st.session_state:
    localizacion, localizacion_var = local(page_name='humedad')
    st.session_state["df_climatico"] = cargar_df(localizacion_var, localidades)
else:
    localizacion, localizacion_var = local(page_name='humedad')
# Filtros principales
df = st.session_state["df_climatico"]

if df is None:
    st.warning("No se ha encontrado el DataFrame. Asegúrate de cargar los datos primero en la página principal.")
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)
st.title(f"🌫️ Humidade Relativa en Galicia")

df_filtrado, año, mes = aplicar_filtros(df)
df_grouped, df_conteo = df_grouped_conteo(df_filtrado)

################# MÉTRICAS PARA TODA GALICIA
# CIUDAD MÁS HUMEDA
# CIUDAD MÁS SECA
# MES MÁS HUMEDO
# MES MÁS SECO
# DÍA MÁS HUMEDO
# DÍA MÁS SECO

df_gal = df_galicia(localidades)
df_kpi = df_gal.groupby("ciudad")


# Ciudad menos humeda
ciudad_menos_humeda, valor_menos_humedo = obtiene_minimo(df_kpi, 'humedad')

# Ciudad más humeda
ciudad_mas_humeda, valor_mas_humedo = obtiene_maximo(df_kpi, 'humedad')


df_temp = df_gal.copy()
# Crear una columna 'mes' en formato año-mes
df_temp["mes"] = df_temp["fecha"].dt.to_period("M")
# Agrupar por mes y sumar la humedad
humedad_por_mes = df_temp.drop('ciudad', axis = 1).groupby("mes")["humedad"].sum()
# Obtener el mes con más humedad
mes_mas_humedado = humedad_por_mes.idxmax()
humedad_total_mes = humedad_por_mes.max()


# Mes más frío (mínima humedad media mensual)
df_temp["mes"] = df_temp["fecha"].dt.to_period("M")

# Mes más humedo, mes menos humedo
min_mes_hum, max_mes_hum = max_min_func(df_temp, 'mes', 'humedad', 'median')
mes_mas_humedo, mes_mas_humedo_valor = max_mes_hum
mes_menos_humedo, mes_menos_humedo_valor = min_mes_hum

# Dia más humedo, dia menos humedo
min_hum, max_hum = max_min_func(df_gal, 'fecha', 'humedad', 'median')
fecha_min, valor_min = min_hum
fecha_max, valor_max = max_hum

# Mostrar métricas
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💧 Ciudad más húmeda", ciudad_mas_humeda, f"{valor_mas_humedo:.2f} %", delta_color="off")
    st.metric("🌵 Ciudad menos húmeda", ciudad_menos_humeda, f"{valor_menos_humedo:.2f} %", delta_color="off")

with col2:
    st.metric("📆🔼 Día más húmedo", pd.to_datetime(fecha_max).strftime("%d %b %Y"), f"{valor_max:.2f} %", delta_color="off")
    st.metric("📆🔽 Día menos húmedo", pd.to_datetime(fecha_min).strftime("%d %b %Y"), f"{valor_min:.2f} %", delta_color="off")
with col3:
    st.metric("📅🔼 Mes más húmedo", str(mes_mas_humedo.strftime("%B %Y")), f"{mes_mas_humedo_valor:.2f} %", delta_color="off")
    st.metric("📅🔽 Mes menos húmedo", str(mes_menos_humedo.strftime("%B %Y")), f"{mes_menos_humedo_valor:.2f} %", delta_color="off")

############################################################################
st.markdown("---")
st.subheader(f"📍 Localización: {localizacion}")
# BARPLOT TEMPERATURA: VARIABLE CATEGÓRICA
# BARPLOT CATEGORICO
categorias = {'Seco 🌵 (<50%)':50, 
              'Moderado 🌤️ (50–75%)':75,
              'Húmedo 💧 (>75%)':100}
colores = {
    'Seco 🌵 (<50%)': 'rgb(204, 204, 204)',  # Gris claro para baja humedad
    'Moderado 🌤️ (50–75%)': 'rgb(102, 153, 255)',  # Azul claro para humedad moderada
    'Húmedo 💧 (>75%)': 'rgb(7, 121, 197)' # Azul fuerte para alta humedad
}

df_hum_cat = df_categorico(df_filtrado, 'humedad', categorias)
fig_bar_hum = fig_bar_humedad(df_hum_cat, colores)
#st.plotly_chart(fig_bar_hum, use_container_width=True)

col1, col2 = st.columns([2, 1])  # 2 partes y 1 parte → 66% y 33%

with col1:
    st.plotly_chart(fig_bar_hum, use_container_width=True)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='custom-container'><h5 style='padding-bottom: 0.1px;';'>🔼 Humedad máxima</h5><h2 >{} %</h2></div>".format(round(df_grouped['humedad'].max(), 2)), unsafe_allow_html=True)
    st.markdown("<div class='custom-container'><h5 style='padding-bottom: 0.1px;';'>➖ Humedad promedio</h5><h2 >{} %</h2></div>".format(round(df_grouped['humedad'].mean(), 2)), unsafe_allow_html=True)
    st.markdown("<div class='custom-container'><h5 style='padding-bottom: 0.1px;';'>🔽 Humedad mínima</h5><h2 >{:.1f} %</h2></div>".format(df_grouped['humedad'].min()), unsafe_allow_html=True)

# LINEA DE HUMEDAD MENSUAL
fig_hume_mes = plot_hum_mes(df_filtrado, localizacion)
st.plotly_chart(fig_hume_mes, use_container_width=True)

# DISTRIBUCIÓN DE HUMEDAD (HISTOGRAMA O UN KDE): Te dice en qué rango de humedad se mueven la mayoría de los días
fig_humidity_kde_clean = plot_humidity_kde_line(df_filtrado, localizacion)
st.plotly_chart(fig_humidity_kde_clean, use_container_width=True)

# LINEA DE HUMEDAD DIARIA: Muestra la evolución temporal y diferencias entre ciudades
fig_humidity_line = plot_humidity_line(df_filtrado, localizacion)
st.plotly_chart(fig_humidity_line, use_container_width=True)

# MAPA DE CALOR (HEATMAP): Muy visual para ver tendencias, anomalías o días con humedad alta/baja
if localizacion_var == "galicia":
    fig_humidity_heatmap = plot_humidity_heatmap(df_filtrado, localizacion)
    st.plotly_chart(fig_humidity_heatmap, use_container_width=True)