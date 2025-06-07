from resources.media_join import video_audio_join, video_join_old as video_join
from resources.generar_voz import generar_voz
from resources.buscar_clips import VideoDownloader
from tests.base_test import BaseTest

class TestSanity_VideoAudioJoin(BaseTest):

    def test_video_audio_join(self):
        video_downloader = VideoDownloader(debug=True)  # Activar mensajes de depuración en la consola
        videos = video_downloader.query(name="food", count=5)
        output_video = video_join(*videos)

        # Ejemplo de uso
        output_audio = generar_voz("Hola, este es un ejemplo de texto a voz.",
                                    output_file="salida.mp3")
        print(f"Archivo MP3 generado en: {output_audio}")

        video_audio_join(*[output_video, output_audio])
