#Ruta más corta en el metro de Medellín - importanto librerías

import pandas as pd
import networkx as nx
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np
from datetime import datetime


# Crear base de datos de conexiones
data = {
    "Origen": [
        "Niquia", "Bello", "Madera", "San Javier", "Estadio", "Suramericana", "Poblado", "Aguacatala", "Itagui", "Sabaneta",
        "San Antonio", "Alpujarra", "Cisneros", "Suramericana", "Estadio", "San Javier", "Poblado", "Aguacatala", "Itagui", "Sabaneta",
        "Acevedo", "Popular", "Santo Domingo Savio", "Andalucia", "San Javier", "Juan 23", "Miraflores", "El Poblado", "San Antonio", "Alpujarra",
        "Cisneros", "Suramericana", "Estadio", "San Javier", "Poblado", "Aguacatala", "Itagui", "Sabaneta"
    ],
    "Destino": [
        "Bello", "Madera", "San Javier", "Estadio", "Suramericana", "Poblado", "Aguacatala", "Itagui", "Sabaneta", "La Estrella",
        "Alpujarra", "Cisneros", "Suramericana", "Estadio", "San Javier", "Poblado", "Aguacatala", "Itagui", "Sabaneta", "La Estrella",
        "Popular", "Santo Domingo Savio", "Andalucia", "La Aurora", "Juan 23", "Vallejuelos", "El Poblado", "San Antonio", "Alpujarra", "Cisneros",
        "Suramericana", "Estadio", "San Javier", "Poblado", "Aguacatala", "Itagui", "Sabaneta", "La Estrella"
    ],
    "Distancia": [
        1500, 1200, 1800, 1300, 1100, 2000, 1400, 1600, 1200, 1000,
        800, 900, 1100, 1300, 1200, 1400, 1500, 1600, 1200, 1000,
        2000, 1800, 1500, 1200, 1300, 1400, 1600, 1200, 800, 900,
        1100, 1300, 1200, 1400, 1500, 1600, 1200, 1000
    ]
}

df_conexiones = pd.DataFrame(data)
METRO = nx.from_pandas_edgelist(df_conexiones, source='Origen', target='Destino', edge_attr='Distancia')

# Generación de datos sintéticos (Supervisados - para datos más realistas se pueden hacer conexiones con la data de las apis públicas de las diferentes agencias gubernamentales)

# ===============================
# Configuración de los datos sintéticos
# ===============================

np.random.seed(42)
n_registros = 5000
estaciones = list(METRO.nodes())
min_dist, max_dist = df_conexiones['Distancia'].min(), df_conexiones['Distancia'].max()

def generar_tiempo_viaje(distancia, hora, lluvia):
    """Función para generar tiempos de viaje realistas"""
    base_time = distancia / 20  # 20 metros por minuto (1.2 km/h)
    
    # Efectos factores externos:
    hora_pico = 1.5 if 7 <= hora <= 9 or 17 <= hora <= 19 else 1.0
    efecto_lluvia = 1.3 if lluvia else 1.0
    
    return base_time * hora_pico * efecto_lluvia * np.random.uniform(0.9, 1.1)

# Generar dataset sintético
data_viajes = []
for _ in range(n_registros):
    origen = np.random.choice(estaciones)
    destinos_posibles = [n for n in METRO.neighbors(origen)]
    
    if not destinos_posibles:
        continue
        
    destino = np.random.choice(destinos_posibles)
    distancia = METRO[origen][destino]['Distancia']
    hora = np.random.randint(0, 24)
    lluvia = np.random.choice([0, 1], p=[0.7, 0.3])
    evento = np.random.choice([0, 1], p=[0.9, 0.1])
    dia_semana = np.random.randint(0, 7)
    
    tiempo = generar_tiempo_viaje(distancia, hora, lluvia)
    
    data_viajes.append({
        'origen': origen,
        'destino': destino,
        'distancia': distancia,
        'hora': hora,
        'dia_semana': dia_semana,
        'lluvia': lluvia,
        'evento': evento,
        'tiempo_viaje': tiempo
    })

df_viajes = pd.DataFrame(data_viajes)

# ======================
# Modelo predictivo
# ======================

# Codificación de estaciones
le = LabelEncoder()
le.fit(estaciones)

X = df_viajes[['origen', 'destino', 'distancia', 'hora', 'dia_semana', 'lluvia', 'evento']].copy()
X['origen'] = le.transform(X['origen'])
X['destino'] = le.transform(X['destino'])
y = df_viajes['tiempo_viaje']

# Escalado de características (excepto las ya codificadas)
scaler = StandardScaler()
cols_escalar = ['distancia', 'hora', 'dia_semana']
X[cols_escalar] = scaler.fit_transform(X[cols_escalar])

# División de datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenamiento del modelo
modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)
modelo_rf.fit(X_train, y_train)

# Evaluación
y_pred = modelo_rf.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"\nError Absoluto Medio del Modelo: {mae:.2f} minutos")

# ========================
# Enrutamiento predictivo
# ========================

def ruta_optima_predictiva(origen, destino, hora_actual=None, condiciones=None):
    #Combina el grafo de NetworkX con el modelo predictivo para:
    # 1. Encontrar la ruta más corta
    # 2. Predecir el tiempo de viaje considerando condiciones actuales

    if hora_actual is None:
        hora_actual = datetime.now().hour
    if condiciones is None:
        condiciones = {'lluvia': 0, 'evento': 0}
    
    # Obtener ruta óptima usando NetworkX
    try:
        ruta = nx.dijkstra_path(METRO, source=origen, target=destino, weight='Distancia')
        distancia_total = nx.dijkstra_path_length(METRO, source=origen, target=destino, weight='Distancia')
    except nx.NetworkXNoPath: print("error: No existe ruta entre las estaciones especificadas")
    
    # Predecir tiempo para cada segmento
    tiempos_segmentos = []
    dia_semana = datetime.now().weekday()
    
    for i in range(len(ruta)-1):
        seg_origen = ruta[i]
        seg_destino = ruta[i+1]
        seg_distancia = METRO[seg_origen][seg_destino]['Distancia']
        
        # Preparar datos para el modelo
        X_segmento = pd.DataFrame([{
            'origen': le.transform([seg_origen])[0],
            'destino': le.transform([seg_destino])[0],
            'distancia': seg_distancia,
            'hora': hora_actual,
            'dia_semana': dia_semana,
            'lluvia': condiciones['lluvia'],
            'evento': condiciones['evento']
        }])
        
        # Escalar características
        X_segmento[cols_escalar] = scaler.transform(X_segmento[cols_escalar])
        
        # Predecir tiempo del segmento
        tiempo_seg = modelo_rf.predict(X_segmento)[0]
        tiempos_segmentos.append(tiempo_seg)
    
    tiempo_total = sum(tiempos_segmentos)
    
    # 3. Resultado integrado
    return {
        'ruta': ruta,
        'distancia_total': distancia_total,
        'tiempo_predicho': tiempo_total,
        'estaciones_intermedias': len(ruta)-2,
        'segmentos': list(zip(ruta[:-1], ruta[1:], tiempos_segmentos))
    }

# ==========
# USO
# ==========

# Condiciones actuales (se puede conectar con la API del IDEAM)
condiciones_actuales = {
    'lluvia': 1,  # 1 = está lloviendo
    'evento': 0   # 0 = no hay eventos especiales
}

# Obtener ruta con predicción
resultado = ruta_optima_predictiva(
    origen="Niquia",
    destino="Estadio",
    hora_actual=18,  # 6 PM (hora pico)
    condiciones=condiciones_actuales
)

print("\nResultado del Sistema Integrado:")
print(f"Ruta recomendada: {' → '.join(resultado['ruta'])}")
print(f"Distancia total: {resultado['distancia_total']} metros")
print(f"Tiempo predicho: {resultado['tiempo_predicho']:.1f} minutos")
print("\nDetalle por segmento:")
for i, (origen, destino, tiempo) in enumerate(resultado['segmentos'], 1):
    print(f"Segmento {i}: {origen} → {destino} | {tiempo:.1f} minutos")
