#!/usr/bin/env python3
# Autores: Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación: 07/06/2026
# Descripción: Generador de datos fisiológicos simulados para alimentar la red de sensores corporales.

import random
import time
from typing import Any, Generator

from utils.physiology_rules import PHYSIOLOGY_RANGES, SENSOR_LAYOUT


def generar_valor_simulado(variable: str) -> tuple[float | str, str]:
    """Genera un valor simulado para una variable fisiológica."""

    if variable == "posture":
        #Contexto de la posición física del paciente. Ayuda a interpretar otras lecturas como pulso o respiración.
        return random.choice(["parado", "sentado", "acostado"]), "clase"

    if variable == "ecg_signal":
        #Señal eléctrica cardiaca simulada. Se deja como señal cruda porque no es una métrica resumida como la FC.
        return round(random.uniform(-1.0, 1.0), 3), "mV"

    if variable in PHYSIOLOGY_RANGES:
        limites = PHYSIOLOGY_RANGES[variable]
        minimo = float(limites["min"])
        maximo = float(limites["max"])
        unidad = str(limites["unit"])

        #Genera un valor aleatorio dentro del rango que esperaríamos en una lectura fisiológica básica.
        valor = round(random.uniform(minimo, maximo), 2)
        return valor, unidad

    return round(random.uniform(0.0, 1.0), 2), "u.a."

def generar_paquete_sensor(sensor_id: str, timestamp: int) -> dict[str, Any]:
    """Genera un paquete individual de lectura para un sensor."""

    configuracion_sensor = SENSOR_LAYOUT[sensor_id]
    variable = random.choice(configuracion_sensor["variables"])
    valor, unidad = generar_valor_simulado(variable)

    #Las llaves del paquete se dejan en inglés para mantener compatibilidad con los demás módulos del proyecto.
    paquete = {
        "sensor_id": sensor_id,
        "sensor_type": configuracion_sensor["type"],
        "zone": configuracion_sensor["zone"],
        "variable": variable,
        "value": valor,
        "unit": unidad,
        "timestamp": timestamp,
    }

    return paquete


def generar_flujo_sensores(
    iteraciones: int = 10,
    pausa: float = 0.5,
) -> Generator[dict[str, Any], None, None]:
    """Genera un flujo de paquetes simulando lecturas de todos los sensores."""

    for timestamp in range(iteraciones):
        for sensor_id in SENSOR_LAYOUT:
            yield generar_paquete_sensor(sensor_id, timestamp)

        #Pausa breve para simular que las lecturas llegan por ventanas de tiempo y no todas de golpe.
        time.sleep(pausa)


def generar_ventana(
    window_id: int,
) -> list[dict[str, Any]]:
    """Genera una ventana de tiempo con una lectura por sensor."""

    return [
        generar_paquete_sensor(sensor_id, window_id)
        for sensor_id in SENSOR_LAYOUT
    ]


# Alias en inglés para mantener compatibilidad con otros módulos del proyecto.
generate_mock_value = generar_valor_simulado
generate_sensor_packet = generar_paquete_sensor
generate_sensor_stream = generar_flujo_sensores
generate_window = generar_ventana


if __name__ == "__main__":
    print("Flujo de datos fisiológicos simulados:\n")

    for paquete in generar_flujo_sensores(iteraciones=3, pausa=0.2):
        print(paquete)