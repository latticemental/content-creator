import os
import logging
import pathlib
import random

from resources.buscar_clips import VideoDownloader
from resources.generar_voz import generar_voz
from resources.media_join import non_audio_video_join as video_join, video_audio_join
from resources.misc_utils import read_yaml_conf

class BaseTest:
    config = read_yaml_conf()

    @classmethod
    def setup_class(cls):
        """before test"""
        cls.logger = logging.getLogger(__name__)
        cls.video_downloader = VideoDownloader(debug=True)

        cls.clean_up_workspace()

    @classmethod
    def teardown_class(cls):
        """after test"""

    @classmethod
    def clean_up_workspace(cls, directory=os.getcwd(), extensions=[".mp3", ".mp4", ".srt"]):
        """Remove any found file with extension specified"""
        # Recorre todos los archivos en el directorio
        for archivo in os.listdir(directory):
            # Obtiene la ruta completa del archivo
            ruta_completa = os.path.join(directory, archivo)

            # Verifica si es un archivo y si tiene una extensión en la lista
            if os.path.isfile(ruta_completa) and any(archivo.endswith(ext) for ext in extensions):
                try:
                    # Intenta eliminar el archivo
                    os.remove(ruta_completa)
                    cls.logger.info(f"Archivo eliminado: {ruta_completa}")
                except Exception as e:
                    cls.logger.warning(f"No se pudo eliminar el archivo {ruta_completa}: {e}")

    def create_video_with_audio(self, keywords: list = ["food"], video_count=2,
                                tts_text: str = "Hola, este es un ejemplo de texto a voz."):
        """ Common function to be used accross many tests to generate video + audio demo"""
        # Descargar y unir video clips
        all_videos = list()
        random.shuffle(keywords)
        for kw in keywords:
            videos = self.video_downloader.query(name=kw, count=video_count)
            all_videos += videos

        output_video = video_join(*all_videos)

        # Generar Texto a Voz (TextToSpeech)
        ruta_absoluta = generar_voz(tts_text,
                                    output_file="salida.mp3")
        self.logger.info(f"Archivo MP3 generado en: {ruta_absoluta}")

        # Unir video + audio
        video_audio_path = video_audio_join(*[output_video, ruta_absoluta])

        return video_audio_path

    def file_exists(self, absolute_path):
        """pathlib.Path().exists()"""
        return pathlib.Path(absolute_path).exists()
