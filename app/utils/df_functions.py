import pandas as pd
import os

def cargar_df(localizacion, localidades):
    df = df_galicia()
    if localizacion.lower() != 'galicia':
        df = df[df["ciudad"] == localidades[localizacion]]

    return df


def df_galicia():
    # Ruta absoluta desde el archivo actual
    base_path = os.path.dirname(os.path.abspath(__file__))  # directorio del script actual
    project_root = os.path.abspath(os.path.join(base_path, '..', '..'))  # sube hasta 'galizia_weather'
    folder = os.path.join(project_root, 'data', 'processed', 'galicia')

    #dataframes = []

    if os.path.exists(folder):
        for archivo in os.listdir(folder):
            path_archivo = os.path.join(folder, archivo)
            df = pd.read_csv(path_archivo, index_col=0, parse_dates=["fecha"])
            #df['ciudad'] = localidades[archivo.split(".")[0]] # columna con nombre de la ciudad
            #dataframes.append(df)
    #df_final = pd.concat(dataframes)
    #df_final["fecha"] = pd.to_datetime(df["fecha"])
    #st.dataframe(df_final, use_container_width=True, height=500)
    return df

def df_grouped_conteo(df):
    df_grouped = df.groupby('fecha').agg({
    'temperatura': 'mean',
    'precipitacion': 'sum',
    'humedad': 'mean'
    }).reset_index()

    df_grouped['llovio'] = df_grouped['precipitacion'] > 0
    df_grouped['mes_anyo'] = df_grouped['fecha'].dt.to_period('M').dt.to_timestamp()
    conteo_con = df_grouped["llovio"].sum()
    conteo_sin = len(df_grouped) - conteo_con
    conteo = [conteo_con, conteo_sin]
    conteo = [conteo_con, conteo_sin]
    etiquetas = ['Días con lluvia 🌧️', 'Días sin lluvia ☀️']

    df_conteo = pd.DataFrame({
        'Tipo de día': etiquetas,
        'Cantidad': conteo
    })
    return df_grouped, df_conteo

def clasificar_temperatura(temp, categorias):
    keys = list(categorias.keys())
    values = list(categorias.values())
    if temp < values[0]:
        return f'{keys[0]}'
    elif temp < values[1]:
        return f'{keys[1]}'
    else:
        return f'{keys[2]}'

def df_categorico(df, col, categorias):
    df_temp = df.copy()
    df_temp['categoria'] = df_temp[col].apply(lambda valor: clasificar_temperatura(valor, categorias))
    df_temp["categoria"] = pd.Categorical(df_temp["categoria"], categories=list(categorias.keys()), ordered=True)
    df_cat = df_temp.groupby("categoria").size().reset_index(name='count')
    return df_cat

def obtiene_maximo(df, col):
    max_id = df[col].median().idxmax()
    maximo = df[col].median().max()
    return max_id, maximo

def obtiene_minimo(df, col):
    min_id = df[col].median().idxmin()
    minimo = df[col].median().min()
    return min_id, minimo

def max_min_dia(df, col):
    df_dias = df.drop('ciudad', axis = 1).groupby("fecha")[col].median()

    # Día de menor valor
    fecha_min = df_dias.idxmin()
    valor_min = df_dias.min()

    # Día de mayor valor
    fecha_max = df_dias.idxmax()
    valor_max = df_dias.max()
    
    return (fecha_min, valor_min), (fecha_max, valor_max)

def max_min_func(df, fecha, col, var):
    if var == 'sum':
        df_fecha = df.drop('ciudad', axis = 1).groupby(fecha)[col].sum()
    if var == 'median':
        df_fecha = df.drop('ciudad', axis = 1).groupby(fecha)[col].median()
    else:
        return "Tu variable no es aceptada, utiliza 'sum' o 'median'"
    # Día de menor valor
    fecha_min = df_fecha.idxmin()
    valor_min = df_fecha.min()

    # Día de mayor valor
    fecha_max = df_fecha.idxmax()
    valor_max = df_fecha.max()
    
    return (fecha_min, valor_min), (fecha_max, valor_max)

def df_forecast(localidades):
    # Ruta absoluta desde el archivo actual
    base_path = os.path.dirname(os.path.abspath(__file__))  # directorio del script actual
    project_root = os.path.abspath(os.path.join(base_path, '..', '..'))  # sube hasta 'galizia_weather'
    folder = os.path.join(project_root, 'data', 'processed', 'forecast')

    dataframes = []

    if os.path.exists(folder):
        for archivo in os.listdir(folder):
            if archivo.endswith('.csv'):
                path_archivo = os.path.join(folder, archivo)
                df = pd.read_csv(path_archivo, index_col=0)
                df["time"] = pd.to_datetime(df["time"])
                df['hora'] = df['time'].dt.hour
                df["hour"] = df['time'].dt.strftime('%H:%M')
                df['city'] = localidades[archivo.split(".")[0]] # columna con nombre de la ciudad
                dataframes.append(df)
    df_final = pd.concat(dataframes)
    #st.dataframe(df_final, use_container_width=True, height=500)
    return df_final
