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
