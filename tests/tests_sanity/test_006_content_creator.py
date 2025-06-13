from tests.base_test import BaseTest
from src.content_media_generator import ContentMediaGenerator_LongFormVideo
from pathlib import Path


class TestContentCreatorClass(BaseTest):
    BaseTest.config["media_src"]["video_template"]
    def test_content_creator_horizontal_usage(self):
        """ContentCreator Usage"""
        longform_video = ContentMediaGenerator_LongFormVideo(output_path="longform_video.mp4")
        output_video = longform_video.create_complete_audiobook(book="Teoria Sintergica",
                                                                author="Jacobo Grinberg",
                                                                video_loop=Path("media_src/template.mp4"),
                                                                video_loop_len=14, # arg to be removed on future versions (video len will be calc automatically)
                                                                duration=5*60,
                                                                music_track=Path("media_src/music_track.mp3"))

        assert self.file_exists(output_video), "Video shall exist!"
