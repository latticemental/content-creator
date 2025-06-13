from .media_toolkit import MediaToolkit
from .content_script_generator import get_script_generator
from pathlib import Path
import math


class SupportedScriptEngines:
    GEMINI = "gemini"
    OPENAI = "openai"


class ContentMediaGenerator_LongFormVideo:
    """
    ContentMediaGenerator_LongFormVideo
    """
    HORIZONTAL_RESOLUTION = "1280x720"
    
    def __init__(self, output_path: Path, script_engine: str = SupportedScriptEngines.GEMINI):
        """
        ContentMediaGenerator_LongFormVideo
        """
        self.script_generator = get_script_generator(script_engine)
        self.media_toolkit = MediaToolkit(output_resolution=self.HORIZONTAL_RESOLUTION)

    def create_complete_audiobook(self, book: str, author: str, duration: int, video_loop: Path, video_loop_len: int, music_track: Path):
        """
        Generates a complete audiobook video using a looping background video.

        This method creates a full-length audiobook from text and narration, 
        overlaying it on a video that will be looped to match the audiobook duration.

        Args:
            book (str): Book name
            author (str): The name of the author of the audiobook.
            duration (int): The total duration of the audiobook in seconds.
            video_loop (Path): Path to the video file to use as the looping background.

        Returns:
            video_path (Path): Filepath to the video created.
        """
        # 1. Generate script base & tts track
        script = self.script_generator.get_audiobook_complete(book, author, duration)
        self.media_toolkit.create_audio_track_mx_male(script)

        content_len = self.media_toolkit.get_content_lenght()
        video_loop_list = [video_loop] * math.ceil(content_len/video_loop_len)

        # 2. Assemble video_loop from template
        self.media_toolkit.join_non_audio_videos(*video_loop_list)

        # 3. Join non_audio_video + tts track
        self.media_toolkit.join_tts_audio_to_video()

        # 4. Join subs to video
        self.media_toolkit.join_tts_subs_to_video()

        # 5. Add music track
        self.media_toolkit.merge_audio_into_video(audio_input=music_track,
                                                  volume_factor=0.3)

        return self.media_toolkit.video_path
    
    def create_audiobook_by_chapter(self, author: str, chapter: int, duration_s: int, video_loop: Path) -> None:
        """
        Generates an audiobook video for a specific chapter using a looping background video.

        This method processes a single chapter of the audiobook and overlays it onto 
        a looping video background for the specified duration.

        Args:
            author (str): The name of the author of the audiobook.
            chapter (int): The chapter number to generate.
            duration_s (int): The duration of the chapter video in seconds.
            video_loop (Path): Path to the video file to use as the looping background.

        Returns:
            video_output_path (Path): Filepath to the video created.
        """

class ContentMediaGenerator_ShortFormVideo:
    """
    ContentMediaGenerator_ShortFormVideo
    """
