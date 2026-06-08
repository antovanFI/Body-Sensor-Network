#!/usr/bin/env python3
# Autores:            Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación:  07/06/2026
# Descripción:        Sistema global de consenso para diagnóstico final unificado

"""
Recibe pre-diagnósticos de múltiples zonas y genera una decisión
consolidada para el estado clínico del paciente.
"""

import time
from threading import Thread
from typing import Any

from consensus.voters import MajorityVoter


class GlobalSystem(Thread):
    """Coordina el consenso entre zonas y publica diagnóstico final."""

    def __init__(self, inbound_queue: Any) -> None:
        """Inicializa cola de entrada y estrategia de consenso global."""
        super().__init__(daemon=True)
        self.inbound_queue = inbound_queue
        self.majority_voter = MajorityVoter()
        
        # Estado de ejecución del hilo de control
        self.running = True
        
        # Buffer distribuido para almacenar el último reporte válido de cada zona
        self.latest_zone_reports: dict[str, dict[str, Any]] = {}
        
        # Listado oficial de zonas del cuerpo humano derivado de physiology_rules.py
        self.expected_zones = {"torax", "brazo_der", "cabeza", "brazo_izq", "piernas"}

    def aggregate_zone_reports(self, reports: list[dict[str, Any]]) -> list[str]:
        """Extrae etiquetas diagnósticas desde reportes zonales válidos.

        Descarta reportes incompletos o fuera de contrato.
        """
        valid_labels: list[str] = []
        
        for r in reports:
            if not r or "local_status" not in r:
                continue
            
            # Extraer el diagnóstico cualitativo ("normal", "warning", "critical")
            status = r["local_status"]
            if status in ["normal", "warning", "critical"]:
                valid_labels.append(status)
                
        return valid_labels

    def emit_global_diagnosis(self, labels: list[str]) -> str:
        """Calcula y retorna diagnóstico final mediante mayoría global."""
        # Invoca MajorityVoter y su resolución por severidad
        return self.majority_voter.choose_diagnosis(labels)

    def stop(self) -> None:
        """Detiene de manera cooperativa el bucle de consumo global."""
        self.running = False

    def run(self) -> None:
        """Bucle de consumo continuo para consolidar diagnósticos."""
        last_consensus_time = time.time()
        consensus_interval = 2.0  # Ejecutar evaluación global cada 2 segundos

        while self.running:
            try:
                # Extraer mensajes de coordinadores de zona (no bloqueante)
                msg = self.inbound_queue.get(timeout=0.1)
            except Exception:
                msg = None

            if msg:
                # Filtrar únicamente los reportes consolidados de zona
                if msg.get("type") == "ZONE_REPORT":
                    zone = msg.get("zone_id")
                    if zone in self.expected_zones:
                        self.latest_zone_reports[zone] = msg

            # Evaluar el estado de salud global de forma periódica
            now = time.time()
            if now - last_consensus_time >= consensus_interval:
                if self.latest_zone_reports:
                    # Convertir el mapa de reportes a una lista plana
                    reports_list = list(self.latest_zone_reports.values())
                    
                    # 1. Agregación y filtrado de etiquetas
                    labels = self.aggregate_zone_reports(reports_list)
                    
                    # 2. Resolución del consenso por mayoría distribuida
                    global_diagnosis = self.emit_global_diagnosis(labels)
                    
                    # 3. Emisión del veredicto final
                    print(f"\n[CONSENSO GLOBAL] Ciclo Evaluado | Cobertura: {len(self.latest_zone_reports)}/{len(self.expected_zones)} zonas")
                    for z, r in self.latest_zone_reports.items():
                        print(f"  -> Zona {z.upper()}: {r['local_status']} (Líder ID: {r['leader_id']})")
                    print(f"  >> DIAGNÓSTICO FINAL DEL CUERPO: {global_diagnosis.upper()}")
                    
                    # Limpiar el buffer para obligar a las zonas a reportar datos nuevos en los próximos 2 segundos.
                    # Si una zona se cae, su ausenciase reflejará en la Cobertura del próximo ciclo.
                    self.latest_zone_reports.clear()

                    # Si se desea mantener un ''caché de red'' de las últimas lecturas, comentar la linea superior.
                
                last_consensus_time = now
