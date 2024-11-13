# Proyecto de API para Procesamiento de Datos de Películas y Sistema de Recomendación

Este proyecto consiste en una API desarrollada en **FastAPI** para disponibilizar datos de películas. La API permite consultar datos procesados y limpiados a partir de archivos CSV (`optimized_movies.csv` y `optimized_credits.csv`). 

Los datos utilizados para la API están en formato CSV y han sido optimizados para reducir el uso de memoria y mejorar el rendimiento:

- **`optimized_movies.csv`**: Contiene información relevante sobre las películas, incluyendo:
  - `id`: Identificador único de cada película.
  - `title`: Título de la película.
  - `release_date`, `release_year`: Fecha y año de lanzamiento.
  - `popularity`, `vote_average`, `vote_count`: Popularidad y puntuaciones.
  - `genres_names`, `overview`: Géneros y descripción de la película, utilizados en la recomendación.
  - `return`, `revenue`, `budget`, `runtime`: Información financiera y duración, necesarias para el análisis exploratorio de datos (EDA) y algunas funciones de la API.

- **`optimized_credits.csv`**: Contiene información sobre el elenco y equipo de cada película, incluyendo:
  - `id`: Identificador único de cada película, para relacionar con `optimized_movies.csv`.
  - `cast_names`, `cast_characters`: Nombres y personajes de los actores.
  - `crew_names`, `crew_jobs`: Nombres y roles de los miembros del equipo, como directores.

## Funcionalidades de la API

La API cuenta con varios endpoints que permiten realizar consultas sobre el conjunto de datos de películas. Los principales endpoints son:

### 1. `GET /cantidad_filmaciones_mes/{mes}`
Devuelve la cantidad de películas estrenadas en un mes específico (en español).

**Ejemplo de respuesta:**
```json
{
  "mensaje": "X cantidad de películas fueron estrenadas en el mes de X"
}
```

### 2. `GET /cantidad_filmaciones_dia/{dia}`
Devuelve la cantidad de películas estrenadas en un día específico de la semana (en español).

**Ejemplo de respuesta:**
```json
{
  "mensaje": "X cantidad de películas fueron estrenadas en los días X"
}
```

### 3. `GET /score_titulo/{titulo}`
Devuelve el título, año de estreno y score de popularidad de una película específica.

**Ejemplo de respuesta:**
```json

{
  "mensaje": "La película X fue estrenada en el año X con un score/popularidad de X"
}
```

### 4. `GET /votos_titulo/{titulo}`
Devuelve el título, cantidad de votos y promedio de votaciones de una película. Requiere que la película tenga al menos 2000 votos para mostrar la información.

**Ejemplo de respuesta:**
```json
{
  "mensaje": "La película X cuenta con un total de X valoraciones, con un promedio de X"
}
```

### 5. `GET /get_actor/{nombre_actor}`
Devuelve la cantidad de películas en las que ha participado un actor, el retorno total y el promedio de retorno por filmación.

**Ejemplo de respuesta:**
```json
{
  "mensaje": "El actor X ha participado de X cantidad de filmaciones, con un retorno total de X y un promedio de X por filmación"
}
```

### 6. GET /get_director/{nombre_director}
Devuelve la cantidad de películas dirigidas por un director, el retorno total y promedio de todas sus películas, y detalles específicos de cada una.

**Ejemplo de respuesta:**
```json
{
  "mensaje": "El director X ha participado en X filmaciones.",
  "retorno_total": X,
  "retorno_promedio": X,
  "detalles_peliculas": [
    {
      "titulo": "Título de la película",
      "fecha_lanzamiento": "Fecha",
      "retorno": X,
      "presupuesto": X,
      "ingresos": X
    },
    {
      "titulo": "Otro título de la película",
      "fecha_lanzamiento": "Otra fecha",
      "retorno": X,
      "presupuesto": X,
      "ingresos": X
    }
  ]
}
```

### 7. GET /get_director/{nombre_director}

La función recomendacion es un sistema de recomendación optimizado que recomienda películas similares basadas en una lista de palabras clave. Esta función:

Filtra las palabras clave más comunes en títulos de películas: "Night", "Day", "Love", "Man", "Girl", "Last", "Movie", "Time", "World".
Precalcula la similitud entre películas utilizando TF-IDF solo con las palabras clave seleccionadas, mejorando el rendimiento.
Almacena las recomendaciones precalculadas en el archivo recommendations.json en la carpeta final_data, permitiendo que la API acceda rápidamente a las recomendaciones sin realizar cálculos intensivos en cada solicitud.

**Ejemplo de respuesta:**
```json
{
  "recomendaciones": ["Película A", "Película B", "Película C", "Película D", "Película E"]
}
```

## Estructura del Proyecto
El proyecto incluye los siguientes archivos y carpetas principales:

**main.py**: Archivo principal de la API, que contiene la configuración de los endpoints.

**final_data/optimized_movies.csv**: Archivo CSV con datos de películas procesados y limpios.

**final_data/optimized_credits.csv**: Archivo CSV con datos de créditos de películas, desanidados y preparados para su uso en la API.

**.gitignore**: Archivo para ignorar archivos innecesarios en el repositorio.
