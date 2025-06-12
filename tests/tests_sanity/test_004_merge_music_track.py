from tests.base_test import BaseTest
from resources.media_join import merge_media


class TestMergeMusicTrack(BaseTest):
    VIDEO_FOR_MUSIC = BaseTest.config["media_src"]["video_for_music"]
    MUSIC_TRACK = BaseTest.config["media_src"]["music_track"]

    def test_add_music_to_video(self):
        """Add music to video"""
        output_video_music_path = merge_media(video_input=self.VIDEO_FOR_MUSIC,
                                              audio_input=self.MUSIC_TRACK,
                                              volume_factor=0.2,
                                              outputfile="video_with_music.mp4")
        assert self.file_exists(output_video_music_path), "Video with Music shall exist!"
