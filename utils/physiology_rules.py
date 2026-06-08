#!/usr/bin/env python3
# Autores: Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación: 07/06/2026
# Descripción: Reglas fisiológicas y definición de rangos normales para pre-diagnóstico clínico (BSN)

from typing import Any


SENSOR_LAYOUT = {
    "sensor_01": {
        "type": "ECG",  # Medidor de frecuencia cardíaca, variabilidad cardíaca y actividad eléctrica del corazón
        "zone": "torax",  # Ubicar sensor entre la base del cuello y el diafragma
        "variables": ["heart_rate", "hrv", "ecg_signal"],
    },
    "sensor_02": {
        "type": "PPG",  # Medidor óptico para pulso periférico y saturación de oxígeno
        "zone": "brazo_der",  # Ubicar sensor en brazo derecho por acceso periférico estable
        "variables": ["spo2", "heart_rate", "pulse"],
    },
    "sensor_03": {
        "type": "Termistor",  # Medidor de temperatura corporal superficial como señal global de referencia
        "zone": "cabeza",  # Ubicar sensor en cabeza/frente
        "variables": ["temperature_c"],
    },
    "sensor_04": {
        "type": "GSR",  # Medidor de conductancia galvánica asociada a actividad del sis. nerv. y sudoración
        "zone": "brazo_izq",  # Ubicar sensor en brazo izquierdo como zona periférica de fácil colocación
        "variables": ["skin_conductance", "humidity"],
    },
    "sensor_05": {
        "type": "IMU",  # Medidor inercial para estimar frecuencia respiratoria y expansión torácica
        "zone": "torax",  # Ubicar sensor en tórax por cercanía directa con la mecánica respiratoria
        "variables": ["resp_rate", "chest_expansion"],
    },
    "sensor_06": {
        "type": "Acelerometro",  # Medidor de movimiento para contextualizar las lecturas del resto de los sensores
        "zone": "piernas",  # Ubicar sensor en extremidades inferiores para detectar actividad y postura
        "variables": ["movement", "posture"],
    },
}


# Rangos fisiológicos de referencia para adultos en reposo.
PHYSIOLOGY_RANGES: dict[str, dict[str, float | str]] = {
    "heart_rate": {"min": 60.0, "max": 100.0, "unit": "bpm"},
    "hrv": {"min": 20.0, "max": 120.0, "unit": "ms"},
    "spo2": {"min": 95.0, "max": 100.0, "unit": "%"},
    "pulse": {"min": 60.0, "max": 100.0, "unit": "bpm"},
    "temperature_c": {"min": 36.1, "max": 37.2, "unit": "°C"},
    "resp_rate": {"min": 12.0, "max": 20.0, "unit": "rpm"},
    "skin_conductance": {"min": 0.5, "max": 10.0, "unit": "uS"},
    "humidity": {"min": 20.0, "max": 80.0, "unit": "%"},
    "chest_expansion": {"min": 0.0, "max": 10.0, "unit": "a.u."},
    "movement": {"min": 0.0, "max": 10.0, "unit": "a.u."},
    "posture": {"min": 0.0, "max": 3.0, "unit": "class"},
}


DIAGNOSIS_SEVERITY: dict[str, int] = {
    "normal": 0,
    "warning": 1,
    "critical": 2,
}


def is_valid_reading(variable: str, value: float) -> bool:
    """Valida si una lectura está dentro del rango fisiológico configurado."""
    limits = PHYSIOLOGY_RANGES.get(variable)

    if limits is None:
        return True

    return float(limits["min"]) <= value <= float(limits["max"])


def evaluate_risk_flags(sample: dict[str, float]) -> list[str]:
    """Genera banderas de riesgo fisiológico a partir de una muestra consolidada."""
    flags = []

    heart_rate = sample.get("heart_rate")
    temperature = sample.get("temperature_c")
    spo2 = sample.get("spo2")
    resp_rate = sample.get("resp_rate")

    if heart_rate is not None and temperature is not None:
        if heart_rate > 100 and temperature > 38:
            flags.append("fever_tachycardia_risk")

    if spo2 is not None and spo2 < 92:
        flags.append("respiratory_risk")

    if resp_rate is not None and resp_rate > 22:
        flags.append("high_respiratory_rate")

    return flags


class PhysiologyRuleEngine:
    """Evalúa muestras fisiológicas según reglas configurables."""

    def classify_sample(self, sample: dict[str, Any]) -> dict[str, Any]:
        violations = []
        score = 0

        for variable, value in sample.items():
            if variable not in PHYSIOLOGY_RANGES:
                continue

            if not is_valid_reading(variable, float(value)):
                violations.append(
                    {
                        "variable": variable,
                        "value": value,
                        "range": PHYSIOLOGY_RANGES[variable],
                    }
                )
                score += 1

        flags = evaluate_risk_flags(sample)

        if score == 0 and not flags:
            status = "normal"
        elif score <= 2:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "violations": violations,
            "risk_flags": flags,
            "score": score,
        }


if __name__ == "__main__":
    engine = PhysiologyRuleEngine()

    test_sample = {
        "heart_rate": 115,
        "temperature_c": 38.5,
        "spo2": 91,
        "resp_rate": 24,
    }

    result = engine.classify_sample(test_sample)
    print(result)