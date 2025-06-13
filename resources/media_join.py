"""This library has been created using DeepSeek"""
import ffmpeg
import os
import logging
import subprocess
from pydub import AudioSegment
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
from resources.subtitles import apply_style_to_ass, convert_srt_to_ass

from resources.misc_utils import time_it

logger = logging.getLogger(__name__)

def _attempt_video_join(*videos, output_resolution="1280x720", output_path="output_joined.mp4", output_fps=30):
    try:
        processed_video_streams = []
        processed_audio_streams = []

        for i, video_path in enumerate(videos):
            input_stream = ffmpeg.input(video_path)

            # Escalar y separar para uso único
            video = input_stream.video.filter('fps', fps=output_fps)
            video = video.filter('scale', *output_resolution.split('x'))

            # Split para generar una rama nueva para cada uso
            video_a = video.filter_multi_output('split')[0]
            processed_video_streams.append(video_a)

            # Manejo de audio o silencio
            try:
                audio = input_stream.audio
                if audio is None:
                    raise ValueError("Audio is None")
            except Exception:
                logger.warning(f"No audio found for {video_path}, using silent fallback.")
                audio = ffmpeg.input('anullsrc', format='lavfi', channel_layout='stereo', sample_rate=44100).audio

            processed_audio_streams.append(audio)

        # Concatenar
        vcat = ffmpeg.concat(*processed_video_streams, v=1, a=0)
        acat = ffmpeg.concat(*processed_audio_streams, v=0, a=1)

        output = ffmpeg.output(vcat, acat, output_path)
        output.run(overwrite_output=True)

        return output_path

    except Exception as e:
        logger.exception("Error joining videos with fallback method")
        raise e

@time_it
def non_audio_video_join(*videos, output_resolution="1280x720", output_path="output_joined.mp4", output_fps=30):
    inputs = [ffmpeg.input(p) for p in videos]

    # Usamos filter_complex con concat n=2, v=1 (video), a=0 (no audio)
    joined = ffmpeg.filter([inpt.video for inpt in inputs], 'concat', n=len(inputs), v=1, a=0)

    # Creamos el output usando el stream concatenado
    out = ffmpeg.output(joined, output_path)

    out.run(overwrite_output=True)

    return output_path

@time_it
def video_join_old(*videos, output_resolution="1280x720", output_path="output_joined.mp4"):
    # Crear una lista de inputs para ffmpeg
    inputs = [ffmpeg.input(video) for video in videos]
    
    # Escalar todos los videos a la misma resolución y forzar SAR 1:1
    scaled_videos = []
    for input_video in inputs:
        scaled_video = input_video.filter('scale', output_resolution).filter('setsar', '1/1')
        scaled_videos.append(scaled_video)
    
    # Concatenar los videos escalados
    concatenated = ffmpeg.concat(*scaled_videos, v=1, a=0)
    
    # Configurar parámetros de salida
    output = concatenated.output(
        output_path,
        vcodec='libx264',
        pix_fmt='yuv420p',
        preset='fast',
        crf=23
    )
    
    # Ejecutar el comando
    output.run(overwrite_output=True)
    
    return output_path

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
def video_join_subs(
    video_input_path: str,
    subtitle_path: str,
    output_path: str,
    margin_v: int = 100,
    font_name: str = "Open Sans",
    font_size: int = 28,
    font_color: str = "&H0032c2f1"
):
    subtitle_path = os.path.abspath(subtitle_path)
    ext = os.path.splitext(subtitle_path)[1].lower()

    if ext == ".srt":
        logger.warning("Los archivos .srt no soportan estilos. Se convertirá a .ass para incrustar estilos.")
        subtitle_path = convert_srt_to_ass(subtitle_path)
        apply_style_to_ass(subtitle_path, margin_v, font_name, font_size, font_color)
    elif ext == ".ass":
        apply_style_to_ass(subtitle_path, margin_v, font_name, font_size, font_color)
    else:
        raise ValueError("El archivo de subtítulo debe ser .srt o .ass")

    try:
        ffmpeg.input(video_input_path).output(
            output_path,
            vf=f"subtitles='{subtitle_path}'",
            **{"c:a": "copy"}
        ).run(overwrite_output=True)

        print(f"Subtítulos incrustados correctamente en: {output_path}")
        return output_path

    except ffmpeg.Error as e:
        print("Error al procesar el video:", e.stderr.decode())

@time_it
def merge_media(video_input, audio_input, outputfile="myfile.mp4", volume_factor=0.0):
    """
    Combina un video con audio existente y un audio adicional.
    Mantiene el audio original del video y mezcla el audio adicional con un volumen reducido.

    Parámetros:
        video_input, audio_input: Rutas de los archivos de entrada (video y audio adicional).
        outputfile: Nombre del archivo de salida.
        volume_factor: Factor de reducción de volumen para el audio adicional (por defecto 0.5).
    """

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

    return os.path.abspath(outputfile)



if __name__ == "__main__":
    from resources.buscar_clips import VideoDownloader

    video_downloader = VideoDownloader(debug=True)  # Activar mensajes de depuración en la consola
    videos = video_downloader.query(name="food", count=2)
    video_join(*videos)