# utils/filters.py
import os
import json
import pandas as pd
import streamlit as st

def cargar_css(path: str):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def coors(localizacion):
    localizacion = localizacion.lower()
    if localizacion == 'galicia':
        coors = [-7.34389, 42.892515]
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))  # directorio del script actual
        project_root = os.path.abspath(os.path.join(base_path, '..', '..'))  # sube hasta 'galizia_weather'
        path = os.path.join(project_root, 'data', 'processed', 'place_coords.json')  # archivo JSON directamente

        with open(path, "r") as f:
            data = json.load(f)
        coors = data[f'{localizacion}']['coors']
    return coors

MESES_ORDENADOS = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def variables_de_tiempo(df):
    df["fecha"] = pd.to_datetime(df["fecha"])
    # Asegúrate de que las columnas necesarias existan
    df["year"] = df["fecha"].dt.year
    df["mes_num"] = df["fecha"].dt.month
    df["mes_nombre"] = df["mes_num"].map(MESES_ORDENADOS)
    df["llovio"] = df["precipitacion"] > 0
    df['mes_anyo'] = df['fecha'].dt.to_period('M')
    return df

def aplicar_filtros(df):
    df = variables_de_tiempo(df)
    # Filtro año
    años = sorted(df["year"].unique(), reverse=True)
    año_seleccionado = st.sidebar.selectbox("Selecciona un año", ["Todos"] + años)

    df_filtrado = df.copy()
    if año_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["year"] == año_seleccionado]

    # Filtro mes
    meses_disponibles = sorted(df_filtrado["mes_num"].unique())
    meses_nombres = [MESES_ORDENADOS[m] for m in [int(i) for i in meses_disponibles[:-1]]]
    mes_seleccionado = st.sidebar.selectbox("Selecciona un mes", ["Todos"] + meses_nombres)

    if mes_seleccionado != "Todos":
        mes_num = [k for k, v in MESES_ORDENADOS.items() if v == mes_seleccionado][0]
        df_filtrado = df_filtrado[df_filtrado["mes_num"] == mes_num]

    return df_filtrado, año_seleccionado, mes_seleccionado



def lluvia_mensual(df_filtrado):
    # Contamos el número total de meses (con datos)
    total_meses = df_filtrado['mes_anyo'].nunique()
    
    precipitaciones_mes = df_filtrado.groupby('mes_nombre')['precipitacion'].sum()

    # Encontramos el mes con más lluvia
    mes_mas_lluvioso = precipitaciones_mes.idxmax()
    lluvia_mas = precipitaciones_mes.max() # VALOR

    # Encontramos el mes con menos lluvia
    mes_menos_lluvioso = precipitaciones_mes.idxmin()
    lluvia_menos = precipitaciones_mes.min() # VALOR 

    return total_meses, mes_mas_lluvioso, mes_menos_lluvioso

#def main(df):
#    df = variables_de_tiempo(df)
#    df, año_seleccionado, mes_seleccionado = aplicar_filtros(df)
#    return df, año_seleccionado, mes_seleccionado