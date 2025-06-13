from tests.base_test import BaseTest
from src.content_media_generator import ContentMediaGenerator_LongFormVideo


class TestContentCreatorClass(BaseTest):
    BaseTest.config["media_src"]["video_template"]
    def test_content_creator_horizontal_usage(self):
        """ContentCreator Usage"""
        longform_video = ContentMediaGenerator_LongFormVideo(output_path="longform_video.mp4")
        longform_video.create_audiobook(author="Jacobo Grinberg",
                                        split_by_chapter=True,
                                        video_loop="media_src/template.mp4",
                                        duration=5*60)
