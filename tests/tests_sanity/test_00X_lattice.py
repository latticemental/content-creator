from tests.base_test import BaseTest
from resources.generar_voz import generar_voz
from resources.media_join import non_audio_video_join, video_audio_join, video_join_subs
from resources.subtitles import generar_subtitulos
from pydub import AudioSegment
import math
import pathlib

class TestGenerateSubs(BaseTest):
    VIDEO_TEMPLATE_PATH = BaseTest.config["src"]["video_template"]
    VIDEO_TEMPLATE_LEN = BaseTest.config["src"]["video_template_len"]

    def test_generate_lattice_sample_video(self):
        """Generate Lattice Sample Video"""
        script = [
            "Bienvenido a Latis Mental, tu canal para explorar la consciencia desde todos sus ángulos.",
            "Hoy viajaremos al corazón de una teoría fascinante y poco conocida: la Lattice de Jacobo Grinberg.",
            "Imagina una red invisible que conecta todo: tu cerebro, tu taza de café y la galaxia más lejana.",
            "¿Y si te dijera que, según Grinberg, esa red es la responsable de la realidad misma?",
            "Jacobo Grinberg fue un neurofisiólogo y psicólogo mexicano, desaparecido misteriosamente en 1994.",
            "Publicó más de 50 libros combinando neurociencia, chamanismo y física cuántica.",
            "Su propuesta central: la existencia de una 'Lattice'—una matriz holográfica de información y energía.",
            "1) La Lattice es un tejido de conciencia que lo abarca todo; no es espacio ni tiempo, sino la base de ellos.",
            "2) Cada punto de la Lattice contiene la información de la totalidad, como un holograma.",
            "3) El cerebro humano actúa como modulador: interpreta esta Lattice y la convierte en la realidad que percibimos.",
            "4) Cuando dos observadores comparten atención, sus cerebros sincronizan patrones y co-colapsan la misma porción de Lattice.",
            "Grinberg describe dos procesos clave:",
            "• Sustracción: el cerebro filtra la Lattice infinita para crear un ‘mapa’ manejable—nuestro mundo cotidiano.",
            "• Adición: mediante prácticas como la meditación o el chamanismo, podemos reducir el filtro y percibir más de la Lattice.",
            "Esto explicaría fenómenos como telepatía, visiones o experiencias cumbre.",
            "En la UNAM, Grinberg midió sincronías en EEG de parejas meditadoras y halló correlaciones aún separados por kilómetros.",
            "Aunque polémicos, esos estudios apuntan a una conexión no-local—exactamente lo que la Lattice predeciría.",
            "La comunidad científica exige replicación y marcos matemáticos sólidos.",
            "Aún no hay consenso, pero la Lattice abre un puente entre ciencia y espiritualidad que merece explorarse.",
            "• Mindfulness: entrenar la atención expande tu acceso a la Lattice.",
            "• Arte y creatividad: estados de flow se interpretan como sintonía con patrones más amplios.",
            "• Terapia: visualizar la interconexión podría fomentar empatía y sanación.",
            "Si este viaje por la Lattice de Jacobo Grinberg te abrió nuevas preguntas, déjalas en los comentarios.",
            "Dale like, comparte este video y suscríbete a Lattice Mental para seguir explorando la consciencia juntos.",
            "¡Hasta la próxima expansión de la realidad!"
        ]
        self.logger.info("1. Creating audio script...")
        audio_path = generar_voz("".join(script),
                                 voz="es-MX-JorgeNeural",
                                 output_file="salida.mp3")
        self.logger.info(f"Archivo MP3 generado en: {audio_path}")
        assert self.file_exists(audio_path), "Expecting MP3 to exist!"

        self.logger.info("2. Creating complete sized video based on MP3 lenght...")
        audio_len = len(AudioSegment.from_file(audio_path))//1000
        self.logger.info(f"Audio lenght in seconds: {audio_len}")

        video_template_repetition = math.ceil(audio_len/self.VIDEO_TEMPLATE_LEN)
        self.logger.info(f"Will join #{video_template_repetition} video_templates to fit {audio_len}")

        assert self.file_exists(self.VIDEO_TEMPLATE_PATH), "Unable to reach video_template!"
        video_list = [self.VIDEO_TEMPLATE_PATH]*video_template_repetition
        non_audio_video_join(*video_list, output_path="output_joined.mp4")

        assert self.file_exists("output_joined.mp4"), "Video with no audio shall exist"
        output_video_path = video_audio_join(*["output_joined.mp4", audio_path])
        assert self.file_exists(output_video_path)

        output_subs_path = generar_subtitulos(output_video_path, "subs.srt")
        assert self.file_exists(output_subs_path), "SRT subtitles shall exist!"

        output_video_subs_path = video_join_subs(video_input_path=output_video_path,
                                                 srt_input_path=output_subs_path,
                                                 output_video="video_with_subs.mp4")
        assert self.file_exists(output_video_subs_path), "Video + SRT shall exist!"
