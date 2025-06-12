from tests.base_test import BaseTest
from content_generator import ContentGenerator_LongFormVideo, ContentGenerator_ShortFormVideo


class TestContentCreatorClass(BaseTest):
    def test_content_creator_horizontal_usage(self):
        """ContentCreator Usage"""
        longform_video = ContentGenerator_LongFormVideo(output_path="longform_video.mp4")
        longform_video.create_audiobook(author="Jacobo Grinberg",
                                        split_by_chapter=True,
                                        duration_s=300)

        assert "longform_video.mp4"

    def test_content_creator_vertical_usage(self):
        """ContentCreator Usage"""
        shortform_video = ContentGenerator_ShortFormVideo(output_path="shortform_video.mp4")
        # To be continued...