import whisper  
import sys
import logging
import pathlib

import cv2
import numpy as np
import pysrt
logger = logging.getLogger(__name__)

def cargar_subtitulos(srt_file):
    """
    Carga los subtítulos desde un archivo .srt.
    """
    subs = pysrt.open(srt_file)
    subtitles = []
    for sub in subs:
        subtitles.append({
            'start': sub.start.ordinal / 1000,  # Convertir a segundos
            'end': sub.end.ordinal / 1000,
            'text': sub.text
        })
    return subtitles

def agregar_subtitulos_a_video(video_file, srt_file, output_file):
    """
    Agrega subtítulos a un video usando OpenCV.
    """
    # Cargar el video
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)  # Cuadros por segundo
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Cargar los subtítulos
    subtitles = cargar_subtitulos(srt_file)
    
    # Crear el escritor para el video de salida
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Formato de compresión
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    
    current_subtitle = None
    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Obtener el tiempo actual del frame (en segundos)
        current_time = frame_index / fps
        
        # Verificar si el subtítulo debe mostrarse
        if current_subtitle is None or current_time > current_subtitle['end']:
            # Buscar el subtítulo más cercano
            for sub in subtitles:
                if current_time >= sub['start'] and current_time <= sub['end']:
                    current_subtitle = sub
                    break
        
        # Si hay un subtítulo para mostrar, agregarlo al frame
        if current_subtitle:
            # Posición y estilo del texto
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            color = (255, 255, 255)  # Blanco
            shadow_color = (0, 0, 0)  # Sombra negra
            thickness = 3
            text_position_y = height - 50  # Colocar 50 píxeles arriba del borde inferior
            
            # Procesar las palabras para subrayar
            word_x = (width - 10 * len(current_subtitle['text'])) // 2  # Centrar el texto
            for i, word in enumerate(current_subtitle['text']):
                # Subrayar la palabra
                word_size = cv2.getTextSize(word, font, font_scale, thickness)[0]
                word_width = word_size[0]
                word_x += i * (word_width + 10)
                
                # Agregar sombra al texto
                cv2.putText(frame, word, (word_x + 2, text_position_y + 2), font, font_scale, shadow_color, thickness + 1)
                
                # Agregar el texto normal
                cv2.putText(frame, word, (word_x, text_position_y), font, font_scale, color, thickness)
                
                # Subrayar la palabra en color amarillo
                word_bottom_left = (word_x, text_position_y + 5)
                word_bottom_right = (word_x + word_width, text_position_y + 5)
                cv2.line(frame, word_bottom_left, word_bottom_right, (0, 255, 255), 2)  # Amarillo
                
                word_x += word_width  # Actualizar posición para la siguiente palabra
        
        # Escribir el frame en el video de salida
        out.write(frame)
        
        frame_index += 1
    
    # Liberar recursos
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video con subtítulos guardado como: {output_file}")

def generar_subtitulos(video_path, output_srt_path="subtitles.srt", model_size="base"):
    """
    Genera un archivo de subtítulos en formato SRT a partir de un video.

    Parámetros:
        video_path (str): Ruta del archivo de video.
        output_srt_path (str): Ruta donde se guardará el archivo SRT (opcional, por defecto "subtitles.srt").
        model_size (str): Tamaño del modelo Whisper ("tiny", "base", "small", "medium", "large").

    Retorna:
        str: Ruta del archivo SRT generado.
    """
    model_size = "base" if sys.platform == "win32" else "small"
    video_path = video_path if sys.platform == "win32" else video_path.replace("\\", "/")  
    # Cargar modelo de Whisper
    logger.info(f"Attempting to load model {model_size}")
    model = whisper.load_model(model_size)

    # Transcribir el audio del video

    logger.info(f"Attempting to transcribe {video_path}")
    result = model.transcribe(video_path)

    # Guardar la transcripción en formato SRT
    with open(output_srt_path, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]

            # Formato SRT (HH:MM:SS,mmm --> HH:MM:SS,mmm)
            f.write(f"{segment['id'] + 1}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{text}\n\n")

    logger.info(f"Subtítulos guardados en: {output_srt_path}")
    return output_srt_path


def format_time(seconds):
    """
    Convierte segundos en formato SRT (HH:MM:SS,mmm).

    Parámetro:
        seconds (float): Tiempo en segundos.

    Retorna:
        str: Tiempo formateado en HH:MM:SS,mmm
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"



# Ejemplo de uso
if __name__ == "__main__":
    generar_subtitulos("video.mp4", "subtitulos.srt")
