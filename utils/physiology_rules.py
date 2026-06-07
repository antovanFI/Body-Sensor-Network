#!/usr/bin/env python3
# Autores:            Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación:  07/06/2026
# Descripción:        Reglas fisiológicas y rangos normales para pre-diagnóstico clínico

from typing import Any

# Rangos de referencia (ejemplo inicial) para adultos en reposo.
PHYSIOLOGY_RANGES: dict[str, dict[str, float]] = {
    "heart_rate": {"min": 60.0, "max": 100.0},
    "spo2": {"min": 95.0, "max": 100.0},
    "temperature_c": {"min": 36.1, "max": 37.2},
    "resp_rate": {"min": 12.0, "max": 20.0},
}

# Mapa simple de severidad para apoyar votación discreta posterior.
DIAGNOSIS_SEVERITY: dict[str, int] = {
    "normal": 0,
    "warning": 1,
    "critical": 2,
}


class PhysiologyRuleEngine:
    """Evalúa muestras fisiológicas según reglas clínicas configurables.

    Lógica esperada:
    - Comparar cada variable con su intervalo normal.
    - Producir etiquetas discretas (normal/alerta/crítico).
    - Incluir trazabilidad de por qué una regla fue activada.
    """

    def classify_sample(self, sample: dict[str, Any]) -> dict[str, Any]:
        """Clasifica una muestra individual en términos diagnósticos.

        Salida sugerida:
        - `status`: etiqueta diagnóstica global.
        - `violations`: lista de variables fuera de rango.
        - `score`: puntuación agregada para decisiones posteriores.
        """
        pass
