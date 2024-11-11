import pandas as pd

# Cargar el archivo CSV original
credits_df = pd.read_csv('DATA/credits.csv')

# Seleccionar una muestra aleatoria del 25% de los datos
sampled_df = credits_df.sample(frac=0.25, random_state=42)

# Guardar el archivo reducido en la misma carpeta
sampled_df.to_csv('DATA/credits_small.csv', index=False)
