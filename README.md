# Proyecto de API para Procesamiento de Datos de Películas

Este proyecto consiste en una API desarrollada en **FastAPI** para disponibilizar datos de películas. La API permite consultar datos procesados y limpiados a partir de archivos CSV (`final_movies.csv` y `final_credits.csv`). 

## Funcionalidades de la API

La API cuenta con varios endpoints que permiten realizar consultas sobre el conjunto de datos de películas. Los principales endpoints son:

### 1. `GET /cantidad_filmaciones_mes/{mes}`
Devuelve la cantidad de películas estrenadas en un mes específico (en español).

**Ejemplo de respuesta:**
```json
{
  "mensaje": "X cantidad de películas fueron estrenadas en el mes de X"
}

### 2. `GET /cantidad_filmaciones_dia/{dia}`
Devuelve la cantidad de películas estrenadas en un día específico de la semana (en español).

**Ejemplo de respuesta:**
```json
{
  "mensaje": "X cantidad de películas fueron estrenadas en los días X"
}

### 3. `GET /score_titulo/{titulo}`
Devuelve el título, año de estreno y score de popularidad de una película específica.

**Ejemplo de respuesta:**
```json

{
  "mensaje": "La película X fue estrenada en el año X con un score/popularidad de X"
}

### 4. `GET /votos_titulo/{titulo}`
Devuelve el título, cantidad de votos y promedio de votaciones de una película. Requiere que la película tenga al menos 2000 votos para mostrar la información.

**Ejemplo de respuesta:**
```json
{
  "mensaje": "La película X cuenta con un total de X valoraciones, con un promedio de X"
}


### 5. `GET /get_actor/{nombre_actor}`
Devuelve la cantidad de películas en las que ha participado un actor, el retorno total y el promedio de retorno por filmación.

**Ejemplo de respuesta:**
```json
{
  "mensaje": "El actor X ha participado de X cantidad de filmaciones, con un retorno total de X y un promedio de X por filmación"
}


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
    ...
  ]
}

## Estructura del Proyecto
El proyecto incluye los siguientes archivos y carpetas principales:

**main.py**: Archivo principal de la API, que contiene la configuración de los endpoints.
**final_data/final_movies.csv**: Archivo CSV con datos de películas procesados y limpios.
**final_data/final_credits.csv**: Archivo CSV con datos de créditos de películas, desanidados y preparados para su uso en la API.
**.gitignore**: Archivo para ignorar archivos innecesarios en el repositorio.
