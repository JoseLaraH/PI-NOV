from fastapi import FastAPI, HTTPException
from datetime import datetime
import pandas as pd
import ast
from starlette.responses import RedirectResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import csv

# Cargar los archivos CSV desde la carpeta final_data
movies_df = pd.read_csv('final_data/optimized_movies.csv', low_memory=False)
credits_df = pd.read_csv('final_data/optimized_credits.csv')

# Cargar el archivo de recomendaciones desde final_data
with open('final_data/recommendations.json', 'r') as f:
    recommendations = json.load(f)

# Convertir `release_date` a formato de fecha para facilitar las consultas
movies_df['release_date'] = pd.to_datetime(movies_df['release_date'], errors='coerce')

# Convertir `id` en ambos DataFrames a string para que sean compatibles al hacer merge
movies_df['id'] = movies_df['id'].astype(str)
credits_df['id'] = credits_df['id'].astype(str)

# Convertir `return`, `budget` y `revenue` a tipo numérico, reemplazando valores no numéricos o nulos por 0
movies_df['return'] = pd.to_numeric(movies_df['return'], errors='coerce').fillna(0)
movies_df['budget'] = pd.to_numeric(movies_df['budget'], errors='coerce').fillna(0)
movies_df['revenue'] = pd.to_numeric(movies_df['revenue'], errors='coerce').fillna(0)

# Asegurar que `crew_names` es una lista de Python real en cada fila
credits_df['crew_names'] = credits_df['crew_names'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
credits_df['crew_jobs'] = credits_df['crew_jobs'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

# Asegurar que `cast_names` es una lista de Python real en cada fila
credits_df['cast_names'] = credits_df['cast_names'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

# Crear la aplicación de FastAPI
app = FastAPI()

# Diccionario para traducir el nombre de los meses en español a número de mes
meses = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

# Diccionario para traducir el nombre de los días en español a número de día (lunes=0, domingo=6)
dias_semana = {
    "lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3,
    "viernes": 4, "sábado": 5, "domingo": 6
}

# Preprocesar los datos de texto para la recomendación
# Crear una columna 'content' combinando título, géneros, y descripción de la película
movies_df['content'] = movies_df['title'] + " " + movies_df['genres_names'] + " " + movies_df['overview']

# Vectorización TF-IDF
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['content'].fillna(''))

# Cálculo de la similitud de coseno
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Crear un índice de títulos para un acceso rápido
indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()


@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes: str):
    # Convertir el nombre del mes a minúsculas para manejar posibles errores de entrada
    mes = mes.lower()
    
    # Obtener el número del mes del diccionario
    mes_numero = meses.get(mes)
    
    # Verificar si el mes ingresado es válido
    if mes_numero is None:
        return {"error": "Mes no válido. Asegúrate de ingresar el mes en español."}
    
    # Filtrar el DataFrame para obtener solo las películas estrenadas en el mes especificado
    cantidad = movies_df[movies_df['release_date'].dt.month == mes_numero].shape[0]
    
    return {"mensaje": f"{cantidad} películas fueron estrenadas en el mes de {mes.capitalize()}"}

@app.get('/cantidad_filmaciones_dia/{dia}')
def cantidad_filmaciones_dia(dia: str):
    # Convertir el nombre del día a minúsculas
    dia = dia.lower()
    
    # Obtener el número del día de la semana
    dia_numero = dias_semana.get(dia)
    
    # Verificar si el día ingresado es válido
    if dia_numero is None:
        return {"error": "Día no válido. Asegúrate de ingresar el día en español."}
    
    # Filtrar el DataFrame para obtener solo las películas estrenadas en el día especificado
    cantidad = movies_df[movies_df['release_date'].dt.weekday == dia_numero].shape[0]
    
    return {"mensaje": f"{cantidad} películas fueron estrenadas en los días {dia.capitalize()}"}

@app.get('/score_titulo/{titulo}')
def score_titulo(titulo: str):
    # Filtrar el DataFrame para obtener la película con el título especificado
    pelicula = movies_df[movies_df['title'].str.lower() == titulo.lower()]
    
    # Verificar si se encontró la película
    if pelicula.empty:
        return {"error": "Película no encontrada. Verifica el título ingresado."}
    
    # Obtener el título, el año de estreno y el score de popularidad
    titulo_pelicula = pelicula.iloc[0]['title']
    año_estreno = pelicula.iloc[0]['release_year']
    score = pelicula.iloc[0]['popularity']
    
    return {
        "mensaje": f"La película '{titulo_pelicula}' fue estrenada en el año {año_estreno} con un score/popularidad de {score}."
    }

@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo: str):
    # Filtrar el DataFrame para obtener la película con el título especificado
    pelicula = movies_df[movies_df['title'].str.lower() == titulo.lower()]
    
    # Verificar si se encontró la película
    if pelicula.empty:
        return {"error": "Película no encontrada. Verifica el título ingresado."}
    
    # Obtener los votos y el promedio de votos
    titulo_pelicula = pelicula.iloc[0]['title']
    votos = pelicula.iloc[0]['vote_count']
    promedio_votos = pelicula.iloc[0]['vote_average']
    
    # Verificar si la cantidad de votos es mayor o igual a 2000
    if votos < 2000:
        return {"mensaje": f"La película '{titulo_pelicula}' no cumple con la condición de 2000 valoraciones."}
    
    return {
        "mensaje": f"La película '{titulo_pelicula}' cuenta con un total de {votos} valoraciones, con un promedio de {promedio_votos}."
    }

@app.get("/recomendacion/{titulo}")
def recomendacion(titulo: str):
    try:
        # Abrir y buscar en el archivo CSV
        with open('final_data/recommendations.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["title"] == titulo:
                    # Extraer las recomendaciones de las columnas
                    recomendaciones = [row[f"recommendation_{i}"] for i in range(1, 6) if row[f"recommendation_{i}"]]
                    return {"recomendaciones": recomendaciones}
        # Si no se encuentra la película
        raise HTTPException(status_code=404, detail="Película no encontrada. Verifica el título ingresado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
