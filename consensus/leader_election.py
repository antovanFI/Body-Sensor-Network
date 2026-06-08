#!/usr/bin/env python3
# Autores:            Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación:  07/06/2026
# Descripción:        Algoritmos de elección de líder para coordinadores zonales

"""
Permite seleccionar dinámicamente un nodo coordinador cuando:
- el líder actual falla,
- se incorpora un nodo con mayor prioridad,
- o se fuerza una reconfiguración de carga.
"""

from typing import Any

class BullyElection:
    """Implementación del algoritmo Bully para la elección distribuida de coordinadores."""

    def __init__(self, node_id: int, peer_ids: list[int], zone_id: str, outbound_queue: Any) -> None:
        """Inicializa identidad del nodo, pares conocidos y canal de comunicación."""
        self.node_id = node_id
        self.peer_ids = peer_ids
        self.zone_id = zone_id
        self.outbound_queue = outbound_queue
        
        # Estado interno del nodo distribuido
        self.current_leader = -1
        self.is_electing = False
        self.received_answer = False

    def start_election(self) -> int:
        """Inicia el proceso de elección enviando mensajes a nodos con mayor ID."""
        self.is_electing = True
        self.received_answer = False
        
        # Filtrar pares en la misma zona con un ID superior
        higher_peers = [pid for pid in self.peer_ids if pid > self.node_id]
        
        if not higher_peers:
            # Si es el nodo con el ID más alto, se proclama líder inmediatamente
            self.announce_coordinator()
            return self.node_id

        # Enviar mensaje de elección a los nodos con mayor jerarquía
        for pid in higher_peers:
            msg = {
                "type": "ELECTION",
                "sender_id": self.node_id,
                "zone_id": self.zone_id
            }
            self.outbound_queue.put(msg)
            
        return self.current_leader

    def handle_election_message(self, sender_id: int) -> None:
        """Procesa mensajes de elección provenientes de nodos con menor ID."""
        if sender_id < self.node_id:
            # Responder al nodo emisor para indicarle que un nodo mayor tomará el control
            msg = {
                "type": "ANSWER",
                "sender_id": self.node_id,
                "zone_id": self.zone_id
            }
            self.outbound_queue.put(msg)
            
            # Si este nodo no estaba en proceso de elección, inicia su propio proceso
            if not self.is_electing:
                self.start_election()

    def handle_answer_message(self, sender_id: int) -> None:
        """Procesa la respuesta de un nodo con mayor ID que frena la proclamación local."""
        if sender_id > self.node_id:
            self.received_answer = True
            self.is_electing = False

    def handle_coordinator_message(self, leader_id: int) -> None:
        """Actualiza el estado local cuando se anuncia el nuevo coordinador de la zona."""
        self.current_leader = leader_id
        self.is_electing = False
        self.received_answer = False

    def announce_coordinator(self) -> None:
        """Proclama la victoria del nodo actual a la zona."""
        self.current_leader = self.node_id
        self.is_electing = False
        
        msg = {
            "type": "COORDINATOR",
            "sender_id": self.node_id,
            "zone_id": self.zone_id
        }
        self.outbound_queue.put(msg)
