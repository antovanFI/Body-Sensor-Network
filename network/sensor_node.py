#!/usr/bin/env python3
# Autores:            Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación:  07/06/2026
# Descripción:        Definición del nodo sensor individual ejecutado en hilo


"""
Cada sensor:
- captura/genera muestras fisiológicas,
- adjunta timestamp lógico Lamport,
- y publica mensajes en colas thread-safe hacia su zona
"""

from threading import Event, Thread
from typing import Any

from utils.concurrency_tools import LamportClock


class SensorNode(Thread):
    """Representa un sensor corporal concurrente dentro de la BSN"""

    def __init__(
        self,
        sensor_id: str,
        zone_id: str,
        outbound_queue: Any,
        lamport_clock: LamportClock,
    ) -> None:
        # Configura identidad, cola de salida y reloj lógico compartido/local
        super().__init__(daemon=True)
        pass

    def collect_sample(self) -> dict[str, Any]:
        # Obtiene una muestra fisiológica del flujo asociado al sensor
        pass

    def build_message(self, sample: dict[str, Any]) -> dict[str, Any]:
        # Construye mensaje de red con metadata causal y de trazabilidad
        pass

    def stop(self) -> None:
        """Solicita detención cooperativa del hilo del sensor."""
        pass

    def run(self) -> None:
        # Bucle principal del sensor: captura, construye mensaje y publica
        pass
