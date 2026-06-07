#!/usr/bin/env python3
# Autores:            Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación:  07/06/2026
# Descripción:        Herramientas de concurrencia para la simulación BSN

"""
Incluye primitivas thread-safe y reloj lógico de Lamport para mantener
orden causal entre eventos distribuidos simulados.
"""

from queue import Queue, Empty
from threading import Lock

class LamportClock:
    """
    Implementación thread-safe del Reloj Lógico de Lamport.
    Asegura que los eventos de los hilos se ordenen causalmente en el sistema distribuido.
    """
    def __init__(self):
        self.time = 0
        self.lock = Lock() # Evita condiciones de carrera al actualizar el reloj

    def tick(self):
        """Llamado cuando ocurre un evento local (ej. un sensor lee un dato)."""
        with self.lock:
            self.time += 1
            return self.time

    def update(self, received_time):
        """Llamado cuando se recibe un mensaje de otro nodo para sincronizar el reloj."""
        with self.lock:
            self.time = max(self.time, received_time) + 1
            return self.time

    def get_time(self):
        """Obtiene el tiempo actual sin incrementarlo."""
        with self.lock:
            return self.time

class ThreadSafeQueue:
    """
    Cola de mensajes segura para hilos. 
    Los Nodos Sensores escribirán aquí y los Coordinadores Zonales leerán de aquí.
    """
    def __init__(self):
        self.q = Queue()

    def put(self, item):
        """Inserta un elemento en la cola."""
        self.q.put(item)

    def get(self, timeout=None):
        """
        Extrae un elemento de la cola. 
        Si hay un timeout y la cola está vacía, retorna None en lugar de bloquearse para siempre.
        """
        try:
            return self.q.get(timeout=timeout)
        except Empty:
            return None

    def is_empty(self):
        """Verifica si la cola está vacía."""
        return self.q.empty()
    