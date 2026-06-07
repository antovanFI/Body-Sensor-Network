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

class BullyElection:
    """Esqueleto del algoritmo Bully para elección de líder.

    Idea base:
    - Cada nodo tiene una prioridad/ID único.
    - Un nodo detecta fallo del líder y notifica a nodos con mayor ID.
    - Si nadie responde, se proclama líder; si responden, espera resultado.
    """

    def __init__(self, node_id: int, peer_ids: list[int]) -> None:
        """Inicializa identidad del nodo y lista de pares conocidos."""
        pass

    def start_election(self) -> int:
        """Inicia proceso de elección y retorna ID del nuevo líder."""
        pass

    def handle_election_message(self, sender_id: int) -> None:
        """Procesa mensajes de elección provenientes de otros nodos."""
        pass

    def handle_coordinator_message(self, leader_id: int) -> None:
        """Actualiza estado local cuando se anuncia nuevo coordinador."""
        pass
