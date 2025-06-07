import os
import asyncio
import edge_tts
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)


async def generar_audio(texto, voz="es-MX-DaliaNeural", output_file="voz_generada.mp3", expected_duration_ms=None):
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
    logger.info(f"Generando voz: {texto}")
    communicate = edge_tts.Communicate(texto, voice=voz)
    
    # Guardar el archivo de audio
    await communicate.save(output_file)
    
    # Si se proporciona expected_duration_ms, ajustar el audio
    if expected_duration_ms is not None:
        # Cargar el archivo de audio
        audio = AudioSegment.from_file(output_file)
        
        # Calcular la duración actual del audio
        current_duration_ms = len(audio)

        logger.info(f"current_duration_ms={current_duration_ms}, expected_duration_ms={expected_duration_ms}")
        # Si el audio es más largo que el tiempo esperado, acelerarlo
        if current_duration_ms > expected_duration_ms and abs(current_duration_ms - expected_duration_ms) > 100:
            # Calcular el factor de aceleración
            speed_factor = current_duration_ms / expected_duration_ms

            if abs(current_duration_ms - expected_duration_ms) > 1250:
                logger.warning(f"WARNING - '{texto}' speed factor is a bit HIGH {speed_factor}")
            
            # Acelerar el audio
            audio = audio.speedup(playback_speed=speed_factor)
        
        # Si el audio es más corto que el tiempo esperado, agregar silencio
        elif current_duration_ms < expected_duration_ms:
            # Calcular la duración del silencio necesario
            silence_duration_ms = expected_duration_ms - current_duration_ms
            if silence_duration_ms > 1000:
                logger.warning(f"WARNING - '{texto}' got silence added for {silence_duration_ms}")
            
            # Generar un segmento de silencio
            silence = AudioSegment.silent(duration=silence_duration_ms)
            logger.info(f"Adding silent segment for {len(silence)}")
            
            # Concatenar el silencio al final del audio
            audio = audio + silence
        
        # Guardar el audio ajustado
        audio.export(output_file, format="mp3")
        logger.info(f"Completed audio duration={len(audio)}")
    
    # Obtener la ruta absoluta
    path_absoluto = os.path.abspath(output_file)
    
    return path_absoluto

# Llamar la función de forma síncrona
def generar_voz(texto, voz="es-MX-DaliaNeural", output_file="voz_generada.mp3", expected_duration_ms=None):
    return asyncio.run(generar_audio(texto, voz, output_file, expected_duration_ms))
if __name__ == "__main__":
    # Ejemplo de uso
    ruta_audio = generar_voz("Hola, este es un ejemplo de voz generada con edge-tts.")
    print(f"Archivo guardado en: {ruta_audio}")
