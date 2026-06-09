#!/usr/bin/env python3
# Autores:            Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación:  08/06/2026
# Descripción:        Punto de entrada de la simulación de Body Sensor Network (BSN)

"""
Este módulo define la orquestación de alto nivel del sistema:
- Inicialización de recursos compartidos (colas seguras, reloj lógico).
- Creación de nodos sensores por zona.
- Activación de coordinadores zonales con elección de líder dinámica.
- Arranque del consenso global para emitir diagnóstico final.
"""

import time
import sys

from consensus.leader_election import BullyElection
from network.global_system import GlobalSystem
from network.sensor_node import SensorNode
from network.zone_coordinator import ZoneCoordinator
from utils.concurrency_tools import LamportClock, ThreadSafeQueue
from utils.physiology_rules import SENSOR_LAYOUT

class SimulationOrchestrator:
    """Orquesta el ciclo de vida completo de la simulación BSN.

    Este controlador central prepara dependencias, construye los hilos
    de cada capa y ejecuta una secuencia de inicio/apagado ordenada.
    """

    def __init__(self) -> None:
        # Inicialización de recursos compartidos y estructuras de control
        self.lamport_clock = LamportClock()
        self.global_queue = ThreadSafeQueue()
        self.zone_queues: dict[str, ThreadSafeQueue] = {}
        
        self.sensors: list[SensorNode] = []
        self.coordinators: list[ZoneCoordinator] = []
        self.global_system: GlobalSystem | None = None
        
        # Extracción de zonas anatómicas únicas desde la configuración
        self.zones = set(config["zone"].lower() for config in SENSOR_LAYOUT.values())

    def build_topology(self) -> None:
        """Construye sensores, coordinadores zonales y sistema global."""
        
        # Se instancia el nodo de consenso central
        self.global_system = GlobalSystem(inbound_queue=self.global_queue)
        
        # Construimos la arquitectura de borde (zonas)
        for zone in self.zones:
            self.zone_queues[zone] = ThreadSafeQueue()
            
            # ==== Prueba 3 ==== -> Comentar de no ser necesaria
            # El tórax tendrá dos coordinadores (ID 1 e ID 2). El resto, solo uno.
            # peer_list = [1, 2] if zone == "torax" else [1]
            
            # Se asigna ID=1 al nodo principal.
            election = BullyElection(
                node_id=1, 
                peer_ids=[1], 
                zone_id=zone, 
                outbound_queue=self.zone_queues[zone]
            )
            
            coordinator = ZoneCoordinator(
                zone_id=zone,
                inbound_queue=self.zone_queues[zone],
                outbound_queue=self.global_queue,
                election=election,
                lamport_clock=self.lamport_clock
            )
            self.coordinators.append(coordinator)
            
            # ==== Prueba 3 ==== -> Comentar de no ser necesaria
            # Instanciar el nodo de respaldo específico para la prueba del algoritmo Bully
            # if zone == "torax":
            #     election_backup = BullyElection(
            #         node_id=2, 
            #         peer_ids=peer_list, 
            #         zone_id=zone, 
            #         outbound_queue=self.zone_queues[zone]
            #     )
            #     coordinator_backup = ZoneCoordinator(
            #         zone_id=zone,
            #         inbound_queue=self.zone_queues[zone],
            #         outbound_queue=self.global_queue,
            #         election=election_backup,
            #         lamport_clock=self.lamport_clock
            #     )
            #     self.coordinators.append(coordinator_backup)
            
        # Se instancian los nodos generadores de datos fisiológicos
        for sensor_id, config in SENSOR_LAYOUT.items():
            zone = config["zone"].lower()
            sensor = SensorNode(
                sensor_id=sensor_id,
                zone=zone,
                logical_clock=self.lamport_clock,
                out_queue=self.zone_queues[zone]
            )
            self.sensors.append(sensor)

    def start(self) -> None:
        """Inicia todos los hilos en el orden correcto."""
        print("==== Iniciando Simulación BSN Distribuida ====")
        
        if self.global_system:
            self.global_system.start()
        
        for coordinator in self.coordinators:
            coordinator.start()
            
        for sensor in self.sensors:
            sensor.start()
            
        print("Hilos en ejecución. Esperando heartbeat y convergencia de líderes (Bully ~3s)...")
        print("Presiona Ctrl+C para detener la simulación.\n")

    def stop(self) -> None:
        """Detiene la simulación de forma segura."""
        print("\n==== Deteniendo simulación de red ====")
        
        # Se transmiten señales de detención cooperativa
        for sensor in self.sensors:
            sensor.stop()
            
        for coordinator in self.coordinators:
            coordinator.stop()
            
        if self.global_system:
            self.global_system.stop()
            
        # Esperar convergencia y cierre de hilos del sistema operativo
        for sensor in self.sensors:
            sensor.join(timeout=1.0)
            
        for coordinator in self.coordinators:
            coordinator.join(timeout=1.0)
            
        if self.global_system:
            self.global_system.join(timeout=1.0)
            
        print("Simulación distribuida finalizada correctamente.")


def main() -> None:
    """Punto de ejecución central."""
    orchestrator = SimulationOrchestrator()
    orchestrator.build_topology()

    try:
        orchestrator.start()
        # ==== Prueba 3 ==== -> Comentar de no ser necesaria
        # segundos = 0
        # Bucle pasivo para mantener el proceso principal activo
        while True:
            time.sleep(1)
            # ==== Prueba 3 ==== -> Comentar de no ser necesaria
            # segundos += 1
            # # Simular la caída catastrófica del servidor principal del tórax a los 10 segundos
            # if segundos == 10:
            #     print("\n==== [FALLO INDUCIDO] Deteniendo nodo Líder del TORAX (ID 2) para forzar algoritmo Bully... ====")
            #     for coord in orchestrator.coordinators:
            #         if coord.zone_id == "torax" and coord.election.node_id == 2:
            #             coord.stop()

    except KeyboardInterrupt:
        orchestrator.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
