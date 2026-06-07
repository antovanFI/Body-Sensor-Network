# Red de Sensores Corporales
Repositorio para realizar el proyecto final que consiste en la Simulación de una Red de Sensores Corporales (BSN) en Python de la materia de Sistemas Distribuidos de la Maestría en Ciencia e Ingeniería de la Computación.

## Estructura de archivos
El proyecto se conforma de la siguiente manera:
```text
body-sensor-network/
  ├── main.py                     # Punto de entrada. Inicia hilos y orquesta la simulación.
  ├── /data
  │   └── dataset_mock.py         # Lector de datos clínicos (PhysioNet/CSV) y generador de flujos.
  ├── /utils
  │   ├── concurrency_tools.py    # Definición de Thread-safe Queues, Locks y el Reloj de Lamport.
  │   └── physiology_rules.py     # Diccionarios con rangos normales y reglas de diagnóstico.
  ├── /consensus
  │   ├── voters.py               # Clases para 'Votador de Mediana' (limpiar ruido continuo) y 'Votador de Mayoría' (diagnóstico).
  │   └── leader_election.py      # Algoritmo de Elección de Líder (ej. algoritmo Bully o Ring) para elegir al coordinador de una zona.
  └── /network
      ├── sensor_node.py          # Hilo de sensor individual. Usa Lamport Clocks y envía a colas seguras.
      ├── zone_coordinator.py     # Nodo líder temporal. Usa voters.py para fusionar datos de su zona y descarta fallos bizantinos.
      └── global_system.py        # Consenso Global. Recibe pre-diagnósticos zonales y emite el diagnóstico final unificado.
```
Donde:
* `main.py` es el punto de entrada del programa, donde se inicializan los hilos de sensores, coordinadores y el sistema global, además de orquestar la simulación.
* La carpeta `data` contiene el módulo para leer datos clínicos simulados y generar flujos de datos para los sensores.
* La carpeta `utils` incluye herramientas de concurrencia (colas seguras, locks) y reglas fisiológicas para diagnóstico.
* La carpeta `consensus` implementa los algoritmos de votación para fusión de datos y la elección de líderes.
* La carpeta `network` define los hilos de los nodos sensores, coordinadores de zona y el sistema global, incluyendo la lógica de comunicación y consenso.

## Equipo 3
- Brito Segura Angel
- Luna Gutierrez Vicente
- Medina Varela Abraham

---
### Instituto de Investigaciones en Matemáticas Aplicadas, UNAM - Semestre 2026-2
