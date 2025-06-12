from tests.base_test import BaseTest
from resources.media_join import video_join_subs
from resources.subtitles import convert_srt_to_ass


class TestGenerateSubs(BaseTest):
    VIDEO_WITH_AUDIO_SRC = BaseTest.config["media_src"]["video_with_audio"]
    SUBTITLES_SRC = BaseTest.config["media_src"]["subtitles_srt"]

    def test_add_subs_to_video(self):
        """Add subs to video"""
        output_subs_ass = convert_srt_to_ass(self.SUBTITLES_SRC, ass_output_path="substitles.ass")
        output_video_subs_path = video_join_subs(video_input_path=self.VIDEO_WITH_AUDIO_SRC,
                                                 subtitle_path=output_subs_ass,
                                                 output_path="video_with_subs.mp4")
        assert self.file_exists(output_video_subs_path), "Video + SRT shall exist!"
