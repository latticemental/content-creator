from resources.generar_voz import generar_voz, EdgeTTS_Voices
from resources.media_join import video_join_subs, video_audio_join, non_audio_video_join, merge_media
from typing import List
from pathlib import Path
from enum import Enum, auto
from pydub import AudioSegment
import logging


class MediaToolkit_WorkflowError(Exception):
    """
    Exception for MediaToolkit
    """


class MediaToolkit_Status(Enum):
    """
    Enumerated Status Workflow for Video Content Creation from TTS track creation (1) to
    final video media with Music + TTS + Video + Subs + Music (5)
    """
    TTS_TRACK = auto()
    NON_AUDIO_VIDEO = auto()
    TTS_AUDIO_VIDEO = auto()
    TTS_AUDIO_VIDEO_SUBS = auto()
    TTS_AUDIO_VIDEO_MUSIC = auto()


class MediaToolkit:
    """
    MediaToolkit
    """
    DEFAULT_SUBTITLES_FILENAME = "subtitles.srt"
    tts_track: Path
    subs_path: Path
    video_path: Path
    music_track: Path

    def __init__(self, output_resolution: str):
        """
        Init MediaToolkit
        """
        self.logger = logging.getLogger()
        self.output_resolution = output_resolution
        self._workflow_status = 0

    def get_content_lenght(self) -> float:
        """
        Get content lenght based on tts_track in seconds
        """
        if not self._workflow_status >= MediaToolkit_Status.TTS_TRACK.value:
            raise MediaToolkit_WorkflowError("No audio track has been created yet! "
                                             f"WORKFLOW_STATUS = {self._workflow_status}")

        return len(AudioSegment.from_file(self.tts_track))/1000

    def _set_workflow_status(self, status: MediaToolkit_Status):
        """
        Set new workflow status
        """
        self.logger.debug(f"Current workflow status: {self._workflow_status}. Updating to: {status.value}")
        self._workflow_status = status.value

    def _create_audio_track(self, txt: str, voice: EdgeTTS_Voices, output_audio: str, output_subs: str):
        """
        Crea una pista de audio usando Edge TTS
        """
        if not self._workflow_status < MediaToolkit_Status.TTS_TRACK.value:
            raise MediaToolkit_WorkflowError("Another audio track has been created already. "
                                             f"WORKFLOW_STATUS = {self._workflow_status}")
        self.subs_path = output_subs
        self.tts_track = generar_voz(txt, voz=voice.value, output_file=output_audio, output_subs=output_subs)

        self.logger.info(f"TTS Audio track created! - output_audio={output_audio}, output_subs={output_subs}")
        self._set_workflow_status(MediaToolkit_Status.TTS_TRACK)

        return self.tts_track

    def create_audio_track_mx_female(self, txt: str, output_audio, output_subs: str = DEFAULT_SUBTITLES_FILENAME) -> Path:
        """
        Crea una pista de audio usando la voz de Mujer -> Dalia
        """
        return Path(self._create_audio_track(txt,
                                             EdgeTTS_Voices.DALIA,
                                             output_audio,
                                             output_subs))
    
    def create_audio_track_mx_male(self, txt: str, output_audio: str, output_subs: str = DEFAULT_SUBTITLES_FILENAME) -> Path:
        """
        Crea una pista de audio usando la voz de Hombre -> Jorge
        """
        return Path(self._create_audio_track(txt,
                                             EdgeTTS_Voices.JORGE,
                                             output_audio,
                                             output_subs))

    def join_non_audio_videos(self, *non_audio_videos: List[Path], output_path: Path) -> Path:
        """
        Combina multiples videos SIN pista de audio
        """
        if not self._workflow_status <= MediaToolkit_Status.NON_AUDIO_VIDEO.value:
            raise MediaToolkit_WorkflowError("Workflow status shall be less or equals to NON_AUDIO_VIDEO. "
                                             "If video already has audio, no other can be joined. "
                                             f"WORKFLOW_STATUS = {self._workflow_status}")

        self.video_path = non_audio_video_join(*non_audio_videos,
                                                    output_resolution=self.output_resolution,
                                                    output_path=output_path)
        self.logger.info("Joined Non Audio videos, a new output video has been created! - "
                         f"output_path={output_path}.")
        self._set_workflow_status(MediaToolkit_Status.NON_AUDIO_VIDEO)

        return self.video_path

    def join_tts_audio_to_video(self):
        """
        Join tts audio track and non audio video
        """
        if not self._workflow_status == MediaToolkit_Status.NON_AUDIO_VIDEO.value:
            raise MediaToolkit_WorkflowError("Workflow status shall be equals to NON_AUDIO_VIDEO. "
                                             f"WORKFLOW_STATUS = {self._workflow_status}")
        output_video = "tts_audio_video.mp4"
        self.video_path = video_audio_join(self.video_path, self.tts_track,
                                           output_resolution=self.output_resolution,
                                           output_path=output_video)

        self.logger.info("Joined TTS Audio to Non Audio video, a new output video has been created! - "
                         f"output_path={self.video_path}.")
        self._set_workflow_status(MediaToolkit_Status.TTS_AUDIO_VIDEO)

        return self.video_path

    def join_videos_with_audio(self, *videos_with_audio: List[Path], output_path: Path) -> Path:
        """
        Combina multiples videos CON pista de audio
        """
        if not self._workflow_status >= MediaToolkit_Status.TTS_AUDIO_VIDEO.value:
            raise MediaToolkit_WorkflowError("Workflow status shall be higher than NON_AUDIO_VIDEO. "
                                             f"WORKFLOW_STATUS = {self._workflow_status}")

        self.video_path = Path(video_audio_join(*videos_with_audio,
                                                output_resolution=self.output_resolution,
                                                output_path=output_path.absolute()))

        self.logger.info("Joined Audio videos, a new output video has been created! - "
                         f"output_path={output_path}.")
        self._set_workflow_status(MediaToolkit_Status.TTS_AUDIO_VIDEO)

        return self.video_path
    
    def join_tts_subs_to_video(self) -> Path:
        """
        Combina un video con audio con los subtitulos previamente generados.
        """
        if not self._workflow_status >= MediaToolkit_Status.TTS_AUDIO_VIDEO.value:
            raise MediaToolkit_WorkflowError("Workflow status shall be higher or equals to TTS_AUDIO_VIDEO. "
                                             f"WORKFLOW_STATUS = {self._workflow_status}")

        output_video = "tts_audio_video_subs.mp4"
        self.video_path = Path(video_join_subs(video_input_path=self.video_path,
                                               subtitle_path=self.subs_path,
                                               output_path=output_video))

        self.logger.info("Joined Subs to video with TTS audio, a new output video has been created! - "
                         f"output_path={output_video}.")
        self._set_workflow_status(MediaToolkit_Status.TTS_AUDIO_VIDEO_SUBS)

        return self.video_path

    def merge_audio_into_video(self, audio_input: Path, volume_factor: int = 0.5) -> Path:
        """
        Combina un video con audio existente y un audio adicional.
        Mantiene el audio original del video y mezcla el audio adicional con un volumen reducido.

        Parámetros:
            audio_input: Ruta del audio de entrada.
            volume_factor: Factor de reducción de volumen para el audio adicional (por defecto 0.5).
        """
        if not self._workflow_status >= MediaToolkit_Status.TTS_AUDIO_VIDEO.value:
            raise MediaToolkit_WorkflowError("Workflow status shall be equals to TTS_AUDIO_VIDEO. "
                                             f"WORKFLOW_STATUS = {self._workflow_status}")

        output_video = "tts_audio_video_music.mp4"
        self.video_path = Path(merge_media(audio_input=audio_input.absolute(),
                                           video_input=self.video_path,
                                           outputfile=output_video,
                                           volume_factor=volume_factor))

        self.logger.info("Joined Music track to video with TTS audio, a new output video has been created! - "
                         f"output_path={output_video}.")
        self._set_workflow_status(MediaToolkit_Status.TTS_AUDIO_VIDEO_MUSIC)

        return self.video_path
