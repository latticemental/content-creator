from tests.base_test import BaseTest
from src.content_script_generator import ContentScriptAIGenerator
from src.media_toolkit import MediaToolkit
import pytest


class TestScriptGeneration(BaseTest):
    BaseTest.config["media_src"]["video_template"]
    def test_script_generation_gemini(self):
        """ContentScriptAIGenerator Usage"""
        toolkit = MediaToolkit(output_resolution="1280x720")
        script_gen = ContentScriptAIGenerator(engine="gemini")
        script = script_gen.get_audiobook_by_chapter(book="Habitos Atomicos",
                                                     author="James Clear",
                                                     chapter=1,
                                                     duration=3*60) # ~3 minutes

        subs_file = "test_script_generation_gemini.srt"
        audio_file = toolkit.create_audio_track_mx_male(script,
                                                        output_audio="test_script_generation_gemini.mp3",
                                                        output_subs=subs_file)

        assert self.file_exists(audio_file), "Audio file shall exist!"
        assert self.file_exists(subs_file), "Subtitles file shall exist!"

    @pytest.mark.skip
    def test_script_generation_openai(self):
        """ContentScriptAIGenerator Usage"""
        toolkit = MediaToolkit(output_resolution="1280x720")
        script_gen = ContentScriptAIGenerator(engine="openai")
        script = script_gen.get_audiobook_complete(book="Habitos Atomicos",
                                                   author="James Clear",
                                                   duration=5*60) # ~5 minutes

        subs_file = "test_script_generation_openai.srt"
        audio_file = toolkit.create_audio_track_mx_male(script,
                                                        output_audio="test_script_generation_openai.mp3",
                                                        output_subs=subs_file)

        assert self.file_exists(audio_file), "Audio file shall exist!"
        assert self.file_exists(subs_file), "Subtitles file shall exist!"
