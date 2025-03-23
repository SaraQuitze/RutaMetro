import pandas as pd
import numpy as np
import networkx as nx


#crear base de datos (las distancias no son reales)
data = {
    "Origen": ["Niquía", "Bello", "Madera", "San Javier", "Estadio", "Suramericana", "Poblado", "Aguacatala", "Itagüí", "Sabaneta"],
    "Destino": ["Bello", "Madera", "San Javier", "Estadio", "Suramericana", "Poblado", "Aguacatala", "Itagüí", "Sabaneta", "La Estrella"],
    "Distancia": [1500, 1200, 1800, 1300, 1100, 2000, 1400, 1600, 1200, 1000]
}
df = pd.DataFrame(data)

print(df)

#se crea la gráfica con los datos entregados
METRO = nx.from_pandas_edgelist(df,source='Origen', target='Destino', edge_attr='Distancia')
METRO.nodes()
METRO.edges()

djk_path= nx.dijkstra_path(METRO, source='Niquia', target='Estadio', weight='Distancia')
djk_path

#lenght (len) contará las estaciones entre destino y fin.
len(djk_path)

#ahora obtendremos la distancia según la información de la tabla
nx.dijkstra_path_length(METRO, 'Niquia', 'Estadio', 'Distancia')

