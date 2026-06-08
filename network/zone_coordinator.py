#!/usr/bin/env python3
# Autores:            Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación:  07/06/2026
# Descripción:        Coordinador temporal de zona para fusión y consenso local

"""
Este nodo líder de zona:
- consume lecturas de sensores de su zona,
- aplica votadores (mediana y mayoría),
- descarta posibles fallos bizantinos básicos,
- y envía pre-diagnósticos al consenso global.
"""

import time
from threading import Thread
from typing import Any

from consensus.leader_election import BullyElection
from consensus.voters import MajorityVoter, MedianVoter
from utils.concurrency_tools import LamportClock
from utils.physiology_rules import PhysiologyRuleEngine


class ZoneCoordinator(Thread):
    """Gestiona el consenso zonal y la salud del liderazgo local."""

    def __init__(
        self,
        zone_id: str,
        inbound_queue: Any,
        outbound_queue: Any,
        election: BullyElection,
        lamport_clock: LamportClock,
    ) -> None:
        
        """Inicializa colas, votadores y estrategia de elección de líder."""
        super().__init__(daemon=True)
        self.zone_id = zone_id.lower()  # Homologar a minúsculas como en SENSOR_LAYOUT
        self.inbound_queue = inbound_queue
        self.outbound_queue = outbound_queue
        self.election = election
        self.lamport_clock = lamport_clock

        # Instanciación de herramientas locales de consenso y reglas
        self.median_voter = MedianVoter()
        self.majority_voter = MajorityVoter()
        self.rule_engine = PhysiologyRuleEngine()

        # Control del estado de la red distribuida
        self.running = True
        self.last_heartbeat_time = time.time()
        self.heartbeat_timeout = 3.0  # Segundos tolerados sin saber del líder
        self.last_heartbeat_sent = 0.0

    def validate_and_group(self, messages: list[dict[str, Any]]) -> dict[str, list[float]]:
        """Filtra mensajes inválidos y agrupa valores por variable."""
        grouped_values: dict[str, list[float]] = {}

        for msg in messages:
            # Sincronización del reloj lógico de Lamport ante eventos de recepción
            if "lamport_timestamp" in msg:
                self.lamport_clock.update(msg["lamport_timestamp"])

            # Descartar payloads malformados o de zonas ajenas al coordinador
            if msg.get("zone_id") != self.zone_id or "data" not in msg:
                continue

            # Agrupar las lecturas por tipo de variable fisiológica
            sensor_data = msg["data"]  # Espera un diccionario ej: {"heart_rate": 72.0}
            for variable, value in sensor_data.items():
                if value is not None:
                    grouped_values.setdefault(variable, []).append(float(value))

        return grouped_values

    def fuse_continuous_signals(self, grouped_values: dict[str, list[float]]) -> dict[str, float]:
        """Aplica `MedianVoter` para obtener consenso por señal continua."""
        fused_signals: dict[str, float] = {}

        for variable, values in grouped_values.items():
            if not values:
                continue
            # Reducción de ruido y aislamiento de fallos bizantinos locales
            fused_signals[variable] = self.median_voter.filter_signal(values)

        return fused_signals

    def vote_diagnosis(self, local_labels: list[str]) -> str:
        """Aplica `MajorityVoter` para etiqueta diagnóstica de zona."""
        return self.majority_voter.choose_diagnosis(local_labels)

    def monitor_leadership(self) -> None:
        """Supervisa latidos del líder y dispara reelección si hay fallo."""
        # Si el proceso actual no es el líder, verifica el timeout del heartbeat
        if self.election.current_leader != self.election.node_id:
            if time.time() - self.last_heartbeat_time > self.heartbeat_timeout:
                if not self.election.is_electing:
                    self.election.start_election()

    def stop(self) -> None:
        """Detiene de forma cooperativa el bucle del hilo."""
        self.running = False

    def run(self) -> None:
        """Bucle principal de coordinación de zona."""
        buffer_mensajes = []
        last_process_time = time.time()

        while self.running:
            # 1. Extrae mensajes de la cola con un timeout no bloqueante
            try:
                msg = self.inbound_queue.get(timeout=0.2)
            except Exception:
                msg = None

            if msg:
                msg_type = msg.get("type")

                # Enruta mensajes de control pertenecientes al algoritmo de elección Bully
                if msg_type in ["ELECTION", "ANSWER", "COORDINATOR"]:
                    if msg.get("zone_id") == self.zone_id:
                        if msg_type == "ELECTION":
                            self.election.handle_election_message(msg["sender_id"])
                        elif msg_type == "ANSWER":
                            self.election.handle_answer_message(msg["sender_id"])
                        elif msg_type == "COORDINATOR":
                            self.election.handle_coordinator_message(msg["sender_id"])
                            self.last_heartbeat_time = time.time()
                
                # Recibe latidos del líder de la zona
                elif msg_type == "HEARTBEAT" and msg.get("zone_id") == self.zone_id:
                    if msg["sender_id"] == self.election.current_leader:
                        self.last_heartbeat_time = time.time()

                # Almacena datos fisiológicos de los sensores concurrentes
                elif msg_type == "DATA":
                    buffer_mensajes.append(msg)

            # 2. Monitorización del estado de la red distributiva
            self.monitor_leadership()

            # 3. Comportamiento periódico como nodo Coordinador - Líder legítimo
            if self.election.current_leader == self.election.node_id:
                now = time.time()
                
                # Emitir un latido periódico hacia los sensores seguidores de su zona (cada 1 segundo)
                if now - self.last_heartbeat_sent >= 1.0:
                    heartbeat = {
                        "type": "HEARTBEAT",
                        "sender_id": self.election.node_id,
                        "zone_id": self.zone_id,
                        "lamport_timestamp": self.lamport_clock.tick()
                    }
                    self.outbound_queue.put(heartbeat)
                    self.last_heartbeat_sent = now

                # Procesar la ventana de tiempo de datos acumulados (cada 2 segundos)
                if now - last_process_time >= 2.0 and buffer_mensajes:
                    # A. Agrupar y filtrar datos concurrentes
                    grouped = self.validate_and_group(buffer_mensajes)
                    
                    # B. Ejecutar fusión distributiva continua (Mediana)
                    fused_features = self.fuse_continuous_signals(grouped)

                    if fused_features:
                        # C. Clasificar la muestra fusionada usando el motor de Vicente
                        classification = self.rule_engine.classify_sample(fused_features)
                        
                        # D. Generar reporte consolidado de zona hacia el Consenso Global
                        reporte_global = {
                            "type": "ZONE_REPORT",
                            "zone_id": self.zone_id,
                            "leader_id": self.election.node_id,
                            "features": fused_features,
                            "local_status": classification["status"],
                            "lamport_timestamp": self.lamport_clock.tick()
                        }
                        self.outbound_queue.put(reporte_global)

                    buffer_mensajes.clear()
                    last_process_time = now
