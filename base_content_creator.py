from resources.generar_voz import generar_voz
from resources.subtitles import generar_subtitulos, convert_srt_to_ass
from resources.media_join import video_join_subs, video_audio_join, non_audio_video_join, merge_media
from typing import List
from pathlib import Path
from enum import Enum
import logging

class EdgeTTS_Voices(Enum):
    DALIA = "es-MX-DaliaNeural"
    JORGE = "es-MX-JorgeNeural"


class BaseContentCreator:
    """
    BaseContentCreator
    """

    def __init__(self, output_resolution):
        """
        Init BaseContentCreator
        """
        self.logger = logging.getLogger()
        self.output_resolution = output_resolution

    def join_non_audio_videos(self, *non_audio_videos: List[Path], output_path: Path) -> Path:
        """
        Combina multiples videos SIN pista de audio
        """
        return Path(non_audio_video_join(*non_audio_videos,
                                         output_resolution=self.output_resolution,
                                         output_path=output_path.absolute()))

    def join_videos_with_audio(self, *videos_with_audio: List[Path], output_path: Path) -> Path:
        """
        Combina multiples videos CON pista de audio
        """
        return Path(video_audio_join(*videos_with_audio,
                                     output_resolution=self.output_resolution,
                                     output_path=output_path.absolute()))

    def merge_audio_into_video(self, audio_input: Path, video_with_audio: Path, output_path: Path,
                               volume_factor: int = 0.5) -> Path:
        """
        Combina un video con audio existente y un audio adicional.
        Mantiene el audio original del video y mezcla el audio adicional con un volumen reducido.

        Parámetros:
            audio_input: Ruta del audio de entrada.
            video_with_audio: Ruta del video con audio existente.
            output_path: Ruta del archivo de salida.
            volume_factor: Factor de reducción de volumen para el audio adicional (por defecto 0.5).
        """
        return Path(merge_media(audio_input=audio_input.absolute(),
                                video_input=video_with_audio.absolute(),
                                outputfile=output_path.absolute(),
                                volume_factor=volume_factor))

    def _create_audio_track(self, txt: str, voice: EdgeTTS_Voices):
        """
        Crea una pista de audio usando Edge TTS
        """
        self.logger.info(f"Creating audio track - voice={voice.name}: {txt}")
        return generar_voz(txt, voz=voice.value)
    
    def create_audio_track_mx_female(self, txt: str) -> Path:
        """
        Crea una pista de audio usando la voz de Mujer -> Dalia
        """
        return Path(self._create_audio_track(txt,
                                             EdgeTTS_Voices.DALIA))
    
    def create_audio_track_mx_male(self, txt: str) -> Path:
        """
        Crea una pista de audio usando la voz de Hombre -> Jorge
        """
        return Path(self._create_audio_track(txt,
                                             EdgeTTS_Voices.JORGE))

    def create_subs_from_video(self, video_with_audio: Path, output_subs_path: Path) -> Path:
        """
        Crea un archivo de subtitulos (ass) de un video CON audio.
        """
        srt_path = generar_subtitulos(video_with_audio,
                                      output_subs_path.absolute().replace("ass", "srt")) # Temp workaround
        return Path(convert_srt_to_ass(srt_path,
                                       output_subs_path.absolute()))
    
    def join_subs_to_video(self, video_with_audio: Path, subtitles: Path) -> Path:
        """
        Combina un video con audio con los subtitulos dados.
        """
        return Path(video_join_subs(video_input_path=video_with_audio.absolute(),
                                    subtitle_path=subtitles.absolute()))


class BaseContentCreatorVertical(BaseContentCreator):
    """
    BaseContentCreatorVertical
    """
    def __init__(self):
        super().__init__(output_resolution="720x1280")
    
    def join_subs_to_video(self, *args, **kwargs):
        self.logger.warning("Vertical Videos require different Subtitles format.")
        raise NotImplementedError


class BaseContentCreatorHorizontal(BaseContentCreator):
    """
    BaseContentCreatorHorizontal
    """
    def __init__(self):
        super().__init__(output_resolution="1280x720")
