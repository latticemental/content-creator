from resources.generar_voz import generar_voz as edgetts_generar_voz
from tests.base_test import BaseTest

class TestTTSAudio(BaseTest):
    def test_audio_edgetts(self):
        audio_path = edgetts_generar_voz("Hola este es un primer test case para generar audio.",
                                         output_file="test_audio1.mp3")

        assert self.file_exists(audio_path), f"Existe {audio_path}"

    def test_audio_edgetts_speedup(self):
        audio_path = edgetts_generar_voz("Hola este es un segundo test case para generar audio.",
                                         output_file="test_audio2.mp3",
                                         expected_duration_ms=2500)

        assert self.file_exists(audio_path), f"Existe {audio_path}"


    def test_audio_edgetts_add_silent(self):
        audio_path = edgetts_generar_voz("Hola este es un tercer test case para generar audio.",
                                         output_file="test_audio3.mp3",
                                         expected_duration_ms=10000)

        assert self.file_exists(audio_path), f"Existe {audio_path}"
