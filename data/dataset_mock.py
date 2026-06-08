#!/usr/bin/env python3
# Autores: Brito Segura Angel, Luna Gutierrez Vicente & Medina Varela Abraham
# Fecha de creación: 07/06/2026
# Descripción: Generador de datos fisiológicos simulados para alimentar la red de sensores corporales.

import random
import time
from pathlib import Path
from typing import Any, Generator

import wfdb

from utils.physiology_rules import PHYSIOLOGY_RANGES, SENSOR_LAYOUT


def generar_valor_simulado(variable: str) -> tuple[float | str, str]:
    """Genera un valor simulado para una variable fisiológica."""

    if variable == "posture":
        #Contexto de la posición física del paciente que contextualiza otras lecturas como pulso o respiración
        return random.choice(["parado", "sentado", "acostado"]), "clase"

    if variable == "ecg_signal":
        #Señal eléctrica cardiaca simulada. Se deja como señal "cruda" porque no es una métrica resumida como la FC
        return round(random.uniform(-1.0, 1.0), 3), "mV"

    if variable in PHYSIOLOGY_RANGES:
        limites = PHYSIOLOGY_RANGES[variable]
        minimo = float(limites["min"])
        maximo = float(limites["max"])
        unidad = str(limites["unit"])

        #Genera un valor aleatorio dentro del rango que esperaríamos en una lectura fisiológica básica
        valor = round(random.uniform(minimo, maximo), 2)
        return valor, unidad

    return round(random.uniform(0.0, 1.0), 2), "u.a."

def generar_paquete_sensor(sensor_id: str, timestamp: int) -> dict[str, Any]:
    """Genera un paquete individual de lectura para un sensor"""

    configuracion_sensor = SENSOR_LAYOUT[sensor_id]
    variable = random.choice(configuracion_sensor["variables"])
    valor, unidad = generar_valor_simulado(variable)

    #Las llaves del paquete se dejan en inglés para mantener compatibilidad. Ya ha sido un problema con mis módulos
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

        #Pausa para simular que las lecturas llegan por ventanas de tiempo y no todas de golpe
        time.sleep(pausa)


def generar_ventana(
    window_id: int,
) -> list[dict[str, Any]]:
    """Genera una ventana de tiempo con una lectura por sensor."""

    return [
        generar_paquete_sensor(sensor_id, window_id)
        for sensor_id in SENSOR_LAYOUT
    ]

def descargar_bidmc(ruta_destino: str = "data/bidmc") -> None:
    """Descarga el dataset BIDMC desde PhysioNet."""

    Path(ruta_destino).mkdir(parents=True, exist_ok=True)

    wfdb.dl_database(
        db_dir="bidmc",
        dl_dir=ruta_destino,
    )


def cargar_registro_bidmc(
    nombre_registro: str = "bidmc01",
    ruta_dataset: str = "data/bidmc",
):
    """""""Carga un registro BIDMC previamente descargado."""

    ruta_registro = str(Path(ruta_dataset) / nombre_registro)
    return wfdb.rdrecord(ruta_registro)


def generar_flujo_bidmc(
    nombre_registro: str = "bidmc01",
    ruta_dataset: str = "data/bidmc",
    limite_muestras: int = 20,
    pausa: float = 0.1,
) -> Generator[dict[str, Any], None, None]:
    """Convierte un registro BIDMC real en paquetes compatibles con la red de sensores."""

    registro = cargar_registro_bidmc(nombre_registro, ruta_dataset)
    #print("Señales disponibles en el registro:", registro.sig_name)

    senales = registro.p_signal
    nombres_senales = registro.sig_name

    mapa_senales = {
        "PLETH": {
            "sensor_id": "sensor_02",
            "sensor_type": "PPG",
            "zone": "brazo_der",
            "variable": "ppg_signal",
            "unit": "u.a.",
        },
        "RESP": {
            "sensor_id": "sensor_05",
            "sensor_type": "IMU",
            "zone": "torax",
            "variable": "resp_signal",
            "unit": "u.a.",
        },
        "II": {
            "sensor_id": "sensor_01",
            "sensor_type": "ECG",
            "zone": "torax",
            "variable": "ecg_signal",
            "unit": "mV",
        },
        "V": {
            "sensor_id": "sensor_01",
            "sensor_type": "ECG",
            "zone": "torax",
            "variable": "ecg_signal",
            "unit": "mV",
        },
    }

    for timestamp, fila in enumerate(senales[:limite_muestras]):
        for indice, nombre_senal in enumerate(nombres_senales):
            nombre_senal = nombre_senal.replace(",", "").strip()

            if nombre_senal not in mapa_senales:
                continue

            base = mapa_senales[nombre_senal]

            paquete = {
                "sensor_id": base["sensor_id"],
                "sensor_type": base["sensor_type"],
                "zone": base["zone"],
                "variable": base["variable"],
                "value": round(float(fila[indice]), 4),
                "unit": base["unit"],
                "timestamp": timestamp,
                "source": "physionet_bidmc",
            }

            yield paquete

        time.sleep(pausa)

def convertir_paquete_a_mensaje_data(
    paquete: dict[str, Any],
    lamport_timestamp: int = 0,
) -> dict[str, Any] | None:
    """Convierte un paquete fisiológico al formato DATA de ZoneCoordinator"""
    #El coordinador sólo fusiona señales en formato de número. Las categóricas (como postura) van por otra vía
    if not isinstance(paquete["value"], (int, float)):
        return None

    return {
        "type": "DATA",#Formato esperado por validate_and_group
        "sender_id": paquete["sensor_id"],
        "zone_id": paquete["zone"],
        "data": {paquete["variable"]: paquete["value"]},
        "unit": paquete["unit"],
        "source_timestamp": paquete["timestamp"],
        "lamport_timestamp": lamport_timestamp,
    }

#Alias en inglés para mantener compatibilidad con otros módulos del proyecto:
generate_mock_value = generar_valor_simulado
generate_sensor_packet = generar_paquete_sensor
generate_sensor_stream = generar_flujo_sensores
generate_window = generar_ventana
download_bidmc = descargar_bidmc #Alias específicos para el uso de datos desde el dataset de physionet
load_bidmc_record = cargar_registro_bidmc
generate_bidmc_stream = generar_flujo_bidmc
convert_packet_to_data_message = convertir_paquete_a_mensaje_data #Alias para compatibilidad con zone_coordinator


if __name__ == "__main__":
    print("Ejemplo de conversión a mensaje DATA:\n")

    # descargar_bidmc()

    paquete_prueba = generar_paquete_sensor("sensor_01", timestamp=1)
    mensaje_data = convertir_paquete_a_mensaje_data(paquete_prueba, lamport_timestamp=1)

    print("Paquete original:")
    print(paquete_prueba)

    #Validación opcional para sensores con variables categóricas como postura.
    #Actualmente la prueba utiliza sensor_01, por lo que siempre debería generar un valor numérico compatible con ZoneCoordinator.

    # if mensaje_data is None:
    #     print("\nEl paquete no se convirtió porque contiene una variable no numérica.")
    # else:
    #     print("\nMensaje compatible con ZoneCoordinator:")
    #     print(mensaje_data)

    print("\nMensaje compatible con ZoneCoordinator:")
    print(mensaje_data)

    print("\nFlujo de datos reales BIDMC:\n")

    for paquete in generar_flujo_bidmc(limite_muestras=5, pausa=0.1):
        print(paquete)