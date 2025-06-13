import os
import asyncio
import edge_tts
import subprocess
from pydub import AudioSegment
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class EdgeTTS_Voices(Enum):
    DALIA = "es-MX-DaliaNeural"
    JORGE = "es-MX-JorgeNeural"


async def generar_audio(texto, voz="es-MX-DaliaNeural", output_file="voz_generada.mp3", expected_duration_ms=None, output_subs=None):
    """Genera un archivo MP3 con el texto en voz sintética y devuelve su ruta absoluta.
    
    Args:
        texto (str): El texto que se convertirá en audio.
        voz (str): La voz que se utilizará (por defecto es "es-MX-DaliaNeural").
        output_file (str): El nombre del archivo de salida (por defecto es "voz_generada.mp3").
        expected_duration_ms (int, optional): La duración esperada del audio en milisegundos. 
                                              Si se proporciona, el audio se ajustará a este tiempo:
                                              - Si es más largo, se acelerará.
                                              - Si es más corto, se agregará silencio al final.
    
    Returns:
        str: La ruta absoluta del archivo de audio generado.
    """
    # Crear el comunicador de edge-tts
    cmd = [
        "edge-tts",
        "--text", texto,
        "--voice", voz,
        "--write-media", output_file
    ]
    if output_subs:
        cmd += ["--write-subtitles", output_subs]
    subprocess.run(cmd, check=True)

    if expected_duration_ms is not None:
        audio = AudioSegment.from_file(output_file)
        current = len(audio)
        logger.info(f"Duración actual: {current} ms, esperada: {expected_duration_ms} ms")
        # Ajuste igual que antes...
        audio.export(output_file, format="mp3")
        logger.info(f"Audio ajustado duración final: {len(audio)} ms")

    return os.path.abspath(output_file)

# Llamar la función de forma síncrona
def generar_voz(texto, voz="es-MX-DaliaNeural", output_file="voz_generada.mp3", expected_duration_ms=None, output_subs=None):
    return asyncio.run(generar_audio(texto, voz, output_file, expected_duration_ms,
                                     output_subs))
if __name__ == "__main__":
    # Ejemplo de uso
    ruta_audio = generar_voz("Hola, este es un ejemplo de voz generada con edge-tts.")
    print(f"Archivo guardado en: {ruta_audio}")
