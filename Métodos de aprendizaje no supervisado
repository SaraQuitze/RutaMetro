#Ruta más corta en el metro de Medellín - importanto librerías

import pandas as pd
import networkx as nx
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from datetime import datetime

# Crear base de datos de conexiones
data = {
    "Origen": ["Niquia", "Bello", "Madera", "San Javier", "Estadio", "Suramericana", "Poblado", "Aguacatala", "Itagui", "Sabaneta"],
    "Destino": ["Bello", "Madera", "San Javier", "Estadio", "Suramericana", "Poblado", "Aguacatala", "Itagui", "Sabaneta", "La Estrella"],
    "Distancia": [1500, 1200, 1800, 1300, 1100, 2000, 1400, 1600, 1200, 1000]
}
df_conexiones = pd.DataFrame(data)
METRO = nx.from_pandas_edgelist(df_conexiones, source='Origen', target='Destino', edge_attr='Distancia')

# Generación de datos sintéticos (no supervisados)
np.random.seed(42)
n_viajes = 2000
estaciones = list(METRO.nodes())

# Generar características no supervisadas (patrones ocultos)
data_viajes = []
for _ in range(n_viajes):
    origen = np.random.choice(estaciones)
    destino = np.random.choice([n for n in METRO.neighbors(origen)])
    distancia = METRO[origen][destino]['Distancia']
    hora = np.random.randint(0, 24)
    dia_semana = np.random.randint(0, 7)
    
    # Patrones ocultos (no usados en supervisado):
    tipo_usuario = np.random.choice(['turista', 'trabajador', 'estudiante'], p=[0.2, 0.6, 0.2])
    dispositivo = np.random.choice(['app', 'tarjeta', 'efectivo'], p=[0.5, 0.4, 0.1])
    
    data_viajes.append({
        'origen': origen,
        'destino': destino,
        'distancia': distancia,
        'hora': hora,
        'dia_semana': dia_semana,
        'tipo_usuario': tipo_usuario,
        'dispositivo': dispositivo
    })

df_viajes = pd.DataFrame(data_viajes)

# Codificación de variables categóricas de los patrones ocultos + df_conexiones
df_encoded = pd.get_dummies(df_viajes, columns=['tipo_usuario', 'dispositivo', 'origen', 'destino'])

# Escalado
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_encoded)


# ========================
# métodos no supervisados
# ========================

# Kmeans agrupará patrones de viaje similares como horario y tipos de usuario
kmeans = KMeans(n_clusters=3, random_state=42)
clusters_kmeans = kmeans.fit_predict(X_scaled)

# Métrica de evaluación
silhouette_kmeans = silhouette_score(X_scaled, clusters_kmeans)
print(f"Silhouette Score (K-Means): {silhouette_kmeans:.2f}")

# dbscan detecta los viajes atípicos u outliers entre las métricas
dbscan = DBSCAN(eps=1.5, min_samples=5)
clusters_dbscan = dbscan.fit_predict(X_scaled)

# tsne revela patrones no lineales entre las relaciones
tsne = TSNE(n_components=2, random_state=42)
X_tsne = tsne.fit_transform(X_scaled)


# ========================
# estandarización de gráficos
# ========================

plt.figure(figsize=(15, 5))

# Gráfico K-Means
plt.subplot(1, 3, 1)
plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=clusters_kmeans, cmap='viridis', alpha=0.6)
plt.title(f'K-Means Clustering (Silhouette: {silhouette_kmeans:.2f})')
plt.colorbar()

# Gráfico DBSCAN
plt.subplot(1, 3, 2)
plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=clusters_dbscan, cmap='viridis', alpha=0.6)
plt.title('DBSCAN Clustering')
plt.colorbar()

# Gráfico de características originales
plt.subplot(1, 3, 3)
plt.scatter(df_viajes['hora'], df_viajes['distancia'], c=clusters_kmeans, cmap='viridis', alpha=0.6)
plt.xlabel('Hora del día')
plt.ylabel('Distancia (m)')
plt.title('Distribución por Hora y Distancia')

plt.tight_layout()
plt.show()

# =====================
# Integración
# =====================

def analizar_patrones(origen, destino, hora_actual=None):
    #Identifica patrones de viaje para una ruta específica
    if hora_actual is None:
        hora_actual = datetime.now().hour
    
    # Filtrar datos para la ruta
    mask = (df_viajes['origen'] == origen) & (df_viajes['destino'] == destino)
    df_ruta = df_viajes[mask].copy()
    
    if len(df_ruta) == 0:
        return {"mensaje": "No hay datos históricos para esta ruta"}
    
    # Asignar clusters a los viajes de esta ruta
    df_ruta_encoded = pd.get_dummies(df_ruta, columns=['tipo_usuario', 'dispositivo'])
    X_ruta = scaler.transform(df_ruta_encoded)
    df_ruta['cluster'] = kmeans.predict(X_ruta)
    
    # Estadísticas por cluster
    stats = df_ruta.groupby('cluster').agg({
        'hora': ['mean', 'std'],
        'distancia': 'mean',
        'tipo_usuario': lambda x: x.mode()[0],
        'dispositivo': lambda x: x.mode()[0]
    }).reset_index()
    
    return {
        'ruta': f"{origen} → {destino}",
        'total_viajes': len(df_ruta),
        'clusters': stats.to_dict('records'),
        'recomendacion': generar_recomendacion(stats, hora_actual)
    }

def generar_recomendacion(stats, hora_actual):
    #Genera recomendaciones basadas en los patrones encontrados
    hora_pico = any(7 <= hora_actual <= 9 or 17 <= hora_actual <= 19)
    
    for cluster in stats.to_dict('records'):
        if cluster['hora']['mean'] - 1 <= hora_actual <= cluster['hora']['mean'] + 1:
            return f"Cluster {cluster['cluster']}: Mayoría de {cluster['tipo_usuario']}s usando {cluster['dispositivo']}"
    
    return "Patrón no identificado. Viaje atípico."

# Uso
resultado_analisis = analizar_patrones("Niquia", "Bello", hora_actual=8)
print("\nAnálisis de Patrones:")
for key, value in resultado_analisis.items():
    print(f"{key}: {value}")
