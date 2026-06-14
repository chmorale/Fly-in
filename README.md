Fly-In Drone Simulation
Este proyecto consiste en una simulación de gestión de tráfico de drones en un entorno de red de zonas conectadas. El objetivo es mover todos los drones desde un start_hub hasta un end_hub respetando las capacidades de las zonas, las restricciones de los pasillos y optimizando las rutas de forma dinámica.

Características Técnicas
Algoritmo de Pathfinding Dinámico: Utiliza un enfoque basado en costes donde:

Las zonas normal tienen un coste base.

Las zonas restricted tienen un coste penalizado para incentivar rutas alternativas.

Las zonas priority actúan como nodos de flujo rápido.

Gestión de Recursos: Control estricto de capacidad máxima (max_drones) tanto en zonas como en conexiones.

Visualización en Tiempo Real: Monitor de terminal que muestra el estado de ocupación de las zonas, el estado de los drones y un log detallado de movimientos por turno.

Sistema de Logs Estricto: Formato de salida compatible con los requisitos de evaluación (droneID-targetZone).

Estructura del Proyecto
fly-in.py: Punto de entrada principal y bucle de simulación.

parser.py: Lógica de lectura y validación del archivo de configuración del mapa.

map.py: Motor de gestión del grafo, conexiones y algoritmos de ruta.

zones.py y connections.py: Definición de los objetos del entorno.

drones.py: Clase gestora del estado y comportamiento de los drones.

Requisitos de Ejecución
El simulador requiere Python 3.10+ y no depende de librerías externas.

Cómo ejecutar:
Asegúrate de tener un archivo my_map.txt en el mismo directorio.

Ejecuta el simulador con:

Bash


python3 fly-in.py
