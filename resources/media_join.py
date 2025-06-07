"""This library has been created using DeepSeek"""
import ffmpeg
import os
import logging
import subprocess
from pydub import AudioSegment
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips

from resources.misc_utils import time_it

logger = logging.getLogger(__name__)

def _attempt_video_join(*videos, output_resolution, output_path):
    # Crear una lista de inputs para ffmpeg
    inputs = [ffmpeg.input(video) for video in videos]
    
    # Escalar todos los videos a la misma resolución
    scaled_videos = []
    for input_video in inputs:
        scaled_video = input_video.video.filter('scale', output_resolution)
        scaled_videos.append(scaled_video)
    
    # Normalizar el audio (misma tasa de muestreo y canales)
    normalized_audios = []
    for input_video in inputs:
        normalized_audio = input_video.audio.filter('aresample', 48000).filter('asetpts', 'PTS-STARTPTS')
        normalized_audios.append(normalized_audio)
    
    # Concatenar los videos escalados
    concatenated_video = ffmpeg.concat(*scaled_videos, v=1, a=0)
    
    # Concatenar los audios normalizados
    concatenated_audio = ffmpeg.concat(*normalized_audios, v=0, a=1)
    
    # Combinar el video y el audio concatenados
    output = ffmpeg.output(concatenated_video, concatenated_audio, output_path)
    
    # Ejecutar el comando de ffmpeg
    output.run(overwrite_output=True)
    
    return output_path

@time_it
def video_join(*videos, output_resolution="1280x720", output_path="output_joined.mp4", output_fps=30):
    # Crear una lista de inputs para ffmpeg
    try:
        inputs = [ffmpeg.input(video) for video in videos]
        
        # Normalizar FPS, escalar resolución y gestionar audio
        processed_videos = []
        processed_audios = []
        
        for i, input_video in enumerate(inputs):
            # Normalizar FPS y escalar video
            processed_video = input_video.video.filter('fps', fps=output_fps).filter('scale', output_resolution)
            processed_videos.append(processed_video)
            
            # Verificar si el video tiene audio
            try:
                if input_video.audio is not None:
                    processed_audios.append(input_video.audio)
                else:
                    silent_audio = ffmpeg.input('anullsrc', format='lavfi', channel_layout='stereo', sample_rate=44100)
                    processed_audios.append(silent_audio.audio)
            except Exception as e:
                logger.warning(f"Error processing audio for video {i}: {e}")
                silent_audio = ffmpeg.input('anullsrc', format='lavfi', channel_layout='stereo', sample_rate=44100)
                processed_audios.append(silent_audio.audio)
        
        # Concatenar videos y audios
        concatenated_video = ffmpeg.concat(*processed_videos, v=1, a=0)
        concatenated_audio = ffmpeg.concat(*processed_audios, v=0, a=1)
        
        # Combinar el video y el audio
        output = ffmpeg.output(concatenated_video, concatenated_audio, output_path)
        output.run()
        
        return output_path
    except AssertionError as error:
        logger.warning("Unable to join using main function. Using _attempt_video_join() instead")
        return _attempt_video_join(*videos, output_resolution, output_path)

@time_it
def video_join_old(*videos, output_resolution="1280x720", output_path="output_joined.mp4"):
    # Crear una lista de inputs para ffmpeg
    try:
        inputs = [ffmpeg.input(video) for video in videos]
        
        # Escalar todos los videos a la misma resolución
        scaled_videos = []
        for input_video in inputs:
            scaled_video = input_video.filter('scale', output_resolution)
            scaled_videos.append(scaled_video)
        
        # Concatenar los videos escalados
        concatenated = ffmpeg.concat(*scaled_videos, v=1, a=0)
        
        # Guardar el video resultante
        concatenated.output(output_path).run()
        
        return output_path
    except Exception as error:
        logger.warning("Unable to join using main function. Using _attempt_video_join() instead")
        return _attempt_video_join(*videos, output_resolution, output_path)

@time_it
def video_add_silent_audio_track(input_video, output_path):
    """
    Agrega una pista de audio de silencio a un video que no tiene audio.

    :param input_video: Ruta del video de entrada.
    :param output_path: Ruta del video de salida con la pista de audio agregada.
    """
    try:
        # Cargar el video de entrada
        input_stream = ffmpeg.input(input_video)

        # Crear un stream de audio silencioso usando anullsrc
        silent_audio = ffmpeg.input(
            'anullsrc=channel_layout=stereo:sample_rate=44100', 
            format='lavfi'
        )

        # Combinar el video con el audio silencioso
        output = ffmpeg.output(
            input_stream.video,  # Stream de video original
            silent_audio,       # Stream de audio silencioso
            output_path,        # Ruta de salida
            vcodec='copy',      # Copiar el códec de video sin re-codificar
            acodec='aac',      # Usar el códec AAC para el audio
            shortest=None      # Asegurar que la salida tenga la duración del video
        )

        # Ejecutar el comando de ffmpeg
        output.run(overwrite_output=True)

        print(f"Video con audio silencioso guardado en: {output_path}")
    except Exception as e:
        print(f"Error al procesar el video: {e}")

@time_it
def video_audio_join(*media, output_resolution="1280x720", output_path="output_with_audio.mp4"):
    # Separar videos y audios
    videos = [m for m in media if m.endswith(('.mp4', '.avi', '.mov'))]
    audios = [m for m in media if m.endswith(('.mp3', '.wav', '.aac'))]
    
    # Crear una lista de inputs para ffmpeg
    video_inputs = [ffmpeg.input(video) for video in videos]
    audio_inputs = [ffmpeg.input(audio) for audio in audios]
    
    # Escalar todos los videos a la misma resolución
    scaled_videos = []
    for input_video in video_inputs:
        scaled_video = input_video.filter('scale', output_resolution)
        scaled_videos.append(scaled_video)
    
    # Concatenar los videos escalados
    concatenated_video = ffmpeg.concat(*scaled_videos, v=1, a=0)
    
    # Concatenar los audios
    concatenated_audio = ffmpeg.concat(*audio_inputs, v=0, a=1)
    
    # Combinar video y audio
    ffmpeg.output(concatenated_video, concatenated_audio, output_path).run()
    logger.info(f"Video joined to audio successfully! - {output_path}")

    return output_path


@time_it
def join_audio(*media, output_file="output.mp3"):
    """
    Une varios archivos de audio MP3 en uno solo.

    :param media: Lista de rutas de archivos MP3.
    :param output_file: Nombre del archivo de salida (por defecto "output.mp3").
    :return: None
    """
    # Crear un objeto AudioSegment vacío
    combined = AudioSegment.empty()

    # Iterar sobre cada archivo de audio
    for audio_file in media:
        # Cargar el archivo MP3
        audio = AudioSegment.from_mp3(audio_file)
        # Añadir el audio al objeto combinado
        combined += audio

    # Exportar el audio combinado a un archivo MP3
    combined.export(output_file, format="mp3")
    print(f"Archivos unidos correctamente en {output_file}")


@time_it
def video_join_subs(video_input_path, srt_input_path, output_video):
    # Convertir rutas a formato absoluto
    video_input_path = video_input_path.replace("\\", "/")
    srt_input_path = srt_input_path.replace("\\", "/")
    
    logger.debug(f"video_input_path={video_input_path}")
    logger.debug(f"srt_input_path={srt_input_path}")

    # 🔹 Verificar si el archivo SRT existe
    if not os.path.exists(srt_input_path.strip('"')):  # Quitar comillas antes de verificar
        print(f"Error: No se encontró el archivo SRT en {srt_input_path}")
        return None

    try:
        # 🔹 Pasar la ruta corregida en comillas dobles
        ffmpeg_cmd = (
            ffmpeg
            .input(video_input_path)
            .output(
                output_video,
                vf=f"subtitles={srt_input_path}",  # Comillas dobles en ruta SRT
                vcodec="libx264",
                acodec="aac",
                strict="experimental"
            )
        )

        # Ejecutar FFmpeg y capturar salida
        ffmpeg_cmd.run(overwrite_output=True, capture_stdout=True, capture_stderr=True)

        return output_video  # Retorna la ruta del video generado

    except ffmpeg.Error as e:
        print("Error al procesar el video:", e.stderr.decode())
        return None  # Retorna None si ocurre un error

@time_it
def merge_media(*media, outputfile="myfile.mp4", volume_factor=0.0):
    """
    Combina un video con audio existente y un audio adicional.
    Mantiene el audio original del video y mezcla el audio adicional con un volumen reducido.

    Parámetros:
        *media: Rutas de los archivos de entrada (video y audio adicional).
        outputfile: Nombre del archivo de salida.
        volume_factor: Factor de reducción de volumen para el audio adicional (por defecto 0.5).
    """
    # Obtener los archivos de entrada
    video_input = media[0]  # Video con audio
    audio_input = media[1]   # Audio adicional

    # Cargar el video y el audio adicional
    video = ffmpeg.input(video_input)
    audio = ffmpeg.input(audio_input)

    # Verificar si el video tiene audio
    video_probe = ffmpeg.probe(video_input)
    video_has_audio = any(stream['codec_type'] == 'audio' for stream in video_probe['streams'])

    # Verificar si el audio adicional es válido
    audio_probe = ffmpeg.probe(audio_input)
    audio_is_valid = any(stream['codec_type'] == 'audio' for stream in audio_probe['streams'])

    if not video_has_audio:
        raise ValueError("El video no contiene una pista de audio válida.")
    if not audio_is_valid:
        raise ValueError("El audio adicional no es válido.")

    # Obtener la duración del video
    video_duration = float(video_probe["format"]["duration"])

    # Procesar el audio adicional
    audio = (
        audio.audio
        .filter('atrim', duration=video_duration)  # Cortar el audio si es más largo que el video
        .filter('volume', volume_factor)  # Reducir el volumen del audio adicional
        .filter('afade', t='out', st=video_duration - 5, d=5)  # Aplicar fade out en los últimos 5 segundos
    )

    # Mezclar el audio original del video con el audio adicional
    merged_audio = ffmpeg.filter([video.audio, audio], 'amix', inputs=2, duration='first')

    # Combinar el video con el audio mezclado
    output = ffmpeg.output(video.video, merged_audio, outputfile, vcodec='copy', acodec='aac')

    # Ejecutar el comando de ffmpeg
    ffmpeg.run(output)



if __name__ == "__main__":
    from resources.buscar_clips import VideoDownloader

    video_downloader = VideoDownloader(debug=True)  # Activar mensajes de depuración en la consola
    videos = video_downloader.query(name="food", count=2)
    video_join(*videos)