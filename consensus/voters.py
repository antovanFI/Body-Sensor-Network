#!/usr/bin/env python3
# Autores:            Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación:  07/06/2026
# Descripción:        Módulo de votadores para tolerancia a fallos y limpieza de ruido

"""
Define dos estrategias de consenso local:
- Votador de mediana: robusto frente a outliers continuos.
- Votador de mayoría: robusto para etiquetas diagnósticas discretas.
"""

from collections import Counter
from typing import Any

class MedianVoter:
    """Fusiona lecturas continuas usando estadística robusta (mediana)."""

    def filter_signal(self, values: list[float]) -> float:
        """Retorna el valor de consenso continuo a partir de `values`."""
        if not values:
            return 0.0  # Evita excepciones en caso de una lista vacía
        
        # Se ordenan los datos para el cálculo de la mediana
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        mid = n // 2
        
        # Se evalúa la longitud (par o impar)
        if n % 2 != 0:
            return float(sorted_vals[mid])
        else:
            return float((sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0)

class MajorityVoter:
    """Fusiona etiquetas discretas por voto mayoritario."""

    def tally(self, labels: list[str]) -> dict[str, int]:
        """Entrega recuento de votos por etiqueta para auditoría."""
        return dict(Counter(labels))

    def choose_diagnosis(self, labels: list[str]) -> str:
        """Retorna la etiqueta diagnóstica consensuada por mayoría."""
        if not labels:
            return "normal"  # Estado por defecto ante ausencia de datos
        
        # Se contabilizan las frecuencias
        counts = self.tally(labels)
        max_votes = max(counts.values())
        
        # Identificamos candidatos con el número máximo de votos
        winners = [label for label, count in counts.items() if count == max_votes]
        
        # Si hay un ganador único, se retorna inmediatamente
        if len(winners) == 1:
            return winners[0]
        
        # Resolución de empates: jerarquía de severidad clínica --> "critical" > "warning" > "normal"
        hierarchy = {"critical": 3, "warning": 2, "normal": 1}
        
        # Se ordenan os ganadores de mayor a menor severidad
        winners_sorted = sorted(winners, key=lambda x: hierarchy.get(x, 0), reverse=True)
        return winners_sorted[0]
