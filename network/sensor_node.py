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

from threading import Thread
from typing import Dict, Any
import time
import random

from utils.concurrency_tools import LamportClock, ThreadSafeQueue
from data.dataset_mock import generar_paquete_sensor, convertir_paquete_a_mensaje_data

class SensorNode(Thread):
    """
    Hilo de ejecución para un sensor fisiológico.
    """
    def __init__(self, sensor_id: str, zone: str, logical_clock: LamportClock, 
                 out_queue: ThreadSafeQueue) -> None:
        """
        Args:
            sensor_id (str): Identificador único del sensor.
            zone (str): Zona anatómica asignada.
            logical_clock (LamportClock): Instancia compartida del reloj lógico.
            out_queue (ThreadSafeQueue): Cola destino para los datos recolectados.
        """
        super().__init__()
        self.sensor_id = sensor_id
        self.zone = zone
        self.clock = logical_clock
        self.out_queue = out_queue
        self.running: bool = True

    def stop(self) -> None:
        """Detiene la ejecución del hilo."""
        self.running = False

    def run(self) -> None:
        """
        Bucle de ejecución del sensor.
        Genera lecturas, timestamp y pone en cola.
        
        Returns:
            None
        """
        while self.running:
            # Reloj avanza porque ocurrió un evento (lectura)
            current_time = self.clock.tick()
            
            # TODO: Debe ser reemplazado por llamadas a dataset_mock.py

            # Generación de dato aleatorio dentro de rangos fisiológicos
            # Se deja comentada para conservar la referencia del primer enfoque.
            #
            # data: Dict[str, Any] = {
            #     "temperatura": round(random.uniform(36.0, 39.0), 1),
            #     "ritmo_cardiaco": int(random.uniform(60, 100))
            # }
            #
            # payload: Dict[str, Any] = {
            #     "timestamp": current_time,
            #     "sensor_id": self.sensor_id,
            #     "zone": self.zone,
            #     "data": data
            # }
            #
            # self.out_queue.put(payload)

            # RESUELTO: La lectura sale desde dataset_mock.py para mantener una sola fuente de datos
            paquete_sensor = generar_paquete_sensor(self.sensor_id, timestamp=current_time)

            payload = convertir_paquete_a_mensaje_data(
                paquete_sensor,
                lamport_timestamp=current_time,
            )

            # Variables como postura no entran al consenso numérico del ZoneCoordinator.
            if payload is not None:
                self.out_queue.put(payload)
                print(f"[{self.zone} - {self.sensor_id}] Dato enviado. Lamport: {current_time}")
            else:
                print(f"[{self.zone} - {self.sensor_id}] Lectura no numérica omitida. Lamport: {current_time}")

            # Esperar un momento antes de la siguiente lectura (simula frecuencia de muestreo)
            time.sleep(random.uniform(0.5, 1.5))