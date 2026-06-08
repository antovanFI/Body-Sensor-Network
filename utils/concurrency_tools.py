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
from typing import Optional, Any

class LamportClock:
    """
    Implementación thread-safe del Reloj Lógico de Lamport.
    Asegura ordenamiento causal en sistemas distribuidos.
    """
    def __init__(self) -> None:
        self.time: int = 0
        self.lock: Lock = Lock()

    def tick(self) -> int:
        """
        Incrementa el reloj local ante un evento.
        
        Returns:
            int: El nuevo valor del reloj tras el tick.
        """
        with self.lock:
            self.time += 1
            return self.time

    def update(self, received_time: int) -> int:
        """
        Sincroniza el reloj local con un tiempo recibido.
        
        Args:
            received_time (int): El timestamp recibido en un mensaje.
            
        Returns:
            int: El nuevo valor del reloj tras la actualización.
        """
        with self.lock:
            self.time = max(self.time, received_time) + 1
            return self.time

class ThreadSafeQueue:
    """
    Cola de mensajes segura para hilos.
    """
    def __init__(self) -> None:
        self.q: Queue = Queue()

    def put(self, item: Any) -> None:
        """
        Inserta un objeto en la cola.
        
        Args:
            item (Any): El mensaje o dato a encolar.
        """
        self.q.put(item)

    def get(self, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Extrae un elemento de la cola de forma segura.
        
        Args:
            timeout (float, optional): Tiempo de espera para obtener datos.
            
        Returns:
            Any: El objeto extraído, o None si la cola está vacía.
        """
        try:
            return self.q.get(timeout=timeout)
        except Empty:
            return None
        