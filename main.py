from fastapi import FastAPI, HTTPException
from datetime import datetime
import pandas as pd
import ast
from starlette.responses import RedirectResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Cargar los archivos CSV desde la carpeta final_data
movies_df = pd.read_csv('final_data/final_movies.csv', low_memory=False)
credits_df = pd.read_csv('final_data/final_credits.csv')

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

@app.get('/get_actor/{nombre_actor}')
def get_actor(nombre_actor: str):
    try:
        # Convertir nombre_actor en minúsculas para una búsqueda insensible a mayúsculas
        nombre_actor = nombre_actor.lower()
        
        # Filtrar el DataFrame de créditos para obtener las películas en las que ha participado el actor
        peliculas_actor = credits_df[credits_df['cast_names'].apply(
            lambda nombres: any(actor.lower() == nombre_actor for actor in nombres) if isinstance(nombres, list) else False
        )]
        
        # Verificar si se encontró el actor en alguna película
        if peliculas_actor.empty:
            raise HTTPException(status_code=404, detail="Actor no encontrado. Verifica el nombre ingresado.")
        
        # Unir los DataFrames para obtener información sobre el retorno de las películas
        peliculas_con_retorno = peliculas_actor.merge(movies_df[['id', 'return']], on='id', how='inner')
        
        # Calcular la cantidad de películas, el retorno total y el retorno promedio
        cantidad_peliculas = peliculas_con_retorno.shape[0]
        retorno_total = peliculas_con_retorno['return'].sum()
        retorno_promedio = retorno_total / cantidad_peliculas if cantidad_peliculas > 0 else 0

        return {
            "mensaje": f"El actor {nombre_actor.capitalize()} ha participado de {cantidad_peliculas} filmaciones, "
                       f"con un retorno total de {retorno_total} y un promedio de {retorno_promedio} por filmación."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")

@app.get('/get_director/{nombre_director}')
def get_director(nombre_director: str):
    try:
        # Convertir nombre_director a minúsculas para búsqueda insensible a mayúsculas
        nombre_director = nombre_director.lower()
        
        # Filtrar `credits_df` para encontrar películas en las que el director trabajó
        peliculas_director = credits_df[
            credits_df['crew_jobs'].apply(
                lambda jobs: "Director" in jobs if isinstance(jobs, list) else False
            ) &
            credits_df['crew_names'].apply(
                lambda names: any(director.lower() == nombre_director for director in names) if isinstance(names, list) else False
            )
        ]
        
        # Verificar si se encontró al director en alguna película
        if peliculas_director.empty:
            raise HTTPException(status_code=404, detail="Director no encontrado. Verifica el nombre ingresado.")
        
        # Unir `peliculas_director` con `movies_df` para obtener datos de cada película
        peliculas_con_retorno = peliculas_director.merge(
            movies_df[['id', 'title', 'release_date', 'return', 'budget', 'revenue']],
            on='id',
            how='inner'
        )
        
        # Calcular el retorno total y el retorno promedio
        retorno_total = peliculas_con_retorno['return'].sum()
        retorno_promedio = retorno_total / peliculas_con_retorno.shape[0] if peliculas_con_retorno.shape[0] > 0 else 0

        # Crear la lista de películas con los detalles solicitados
        detalles_peliculas = peliculas_con_retorno.apply(
            lambda row: {
                "titulo": row['title'],
                "fecha_lanzamiento": row['release_date'],
                "retorno": row['return'],
                "presupuesto": row['budget'],
                "ingresos": row['revenue']
            },
            axis=1
        ).tolist()
        
        return {
            "mensaje": f"El director {nombre_director.capitalize()} ha participado en {peliculas_con_retorno.shape[0]} filmaciones.",
            "retorno_total": retorno_total,
            "retorno_promedio": retorno_promedio,
            "detalles_peliculas": detalles_peliculas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")
    
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/recomendacion/{titulo}")
def recomendacion(titulo: str):
    # Comprobar si la película existe en el conjunto de datos
    if titulo not in indices:
        raise HTTPException(status_code=404, detail="Película no encontrada. Verifica el título ingresado.")

    # Obtener el índice de la película solicitada
    idx = indices[titulo]

    # Obtener la lista de similitud de la película con todas las demás
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Ordenar las películas según el puntaje de similitud (de mayor a menor)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Obtener los índices de las 5 películas más similares (excluyendo la película solicitada)
    sim_scores = sim_scores[1:6]
    movie_indices = [i[0] for i in sim_scores]

    # Devolver los títulos de las 5 películas más similares
    recomendaciones = movies_df['title'].iloc[movie_indices].tolist()
    return recomendaciones