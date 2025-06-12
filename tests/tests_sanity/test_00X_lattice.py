from tests.base_test import BaseTest
from resources.generar_voz import generar_voz
from resources.media_join import non_audio_video_join, video_audio_join, video_join_subs, merge_media
from pydub import AudioSegment
import math
import pathlib

class TestGenerateSubs(BaseTest):
    VIDEO_TEMPLATE_PATH = BaseTest.config["media_src"]["video_template"]
    VIDEO_TEMPLATE_LEN = BaseTest.config["media_src"]["video_template_len"]

    def test_generate_lattice_sample_video(self):
        """Generate Lattice Sample Video"""
        script = [
            # INICIO
            "Imaginemos un enrejado invisible que conecta todo el Universo… Eso es la ‘Lattice’. "
            "En el capítulo 1, Grinberg la presenta como una estructura fundamental del espacio-tiempo, "
            "hipercompleja, simétrica y coherente; una matriz energética que contiene toda la información del cosmos en cada punto.",

            "No hay huecos en esta red: hasta el vacío mismo rebosa de información. La materia —ya sea una partícula o un cristal— "
            "es simplemente una modulación local de esta estructura. Así lo describe Grinberg: cada punto de la Lattice, "
            "incluso si no lo percibimos, contiene la totalidad del universo.",

            # DESARROLLO
            "El cerebro no es solo un receptor: es una lente que distorsiona la Lattice. Cada neurona activa cambia un poco "
            "la estructura de esa red. El conjunto de esas alteraciones se llama campo neuronal —la base de la percepción que experimentamos.",

            "Grinberg introduce el concepto clave de ‘sintergia’, fusión de síntesis y energía, definida por: coherencia, "
            "densidad informacional y frecuencia. Presume que cuanto más alta es la sintergia, más refinada y profunda es "
            "la interacción entre Lattice y campo neuronal.",

            "Sostiene que nuestra realidad perceptual —colores, formas, sonidos— no es la realidad 'ahí afuera', sino una construcción "
            "neuronal sobre esa matriz universal. Según él, la percepción es siempre una representación y nunca la realidad en sí.",

            # CIERRE
            "Para Grinberg, la Lattice en estado puro es conciencia pura, sin forma, sin materia, sin tiempo. "
            "Solo cuando nuestro cerebro interviene —al distorsionarla— emergen el tiempo, los objetos y la percepción.",

            "El capítulo sugiere que un cerebro altamente coherente, de alta sintergia, podría resonar con la Lattice en su estado original, "
            "induciendo un estado de Unidad, donde el ego desaparece y la conciencia se fusiona con el todo.",

            "Lo que no está del todo claro en este capítulo es cómo se mide o cuantifica la sintergia de forma práctica, "
            "y qué tipo de entrenamiento mental —si existe— facilita esa resonancia profunda. Grinberg insinúa que culturas ancestrales "
            "y técnicas chamánicas podrían explorar esos estados, pero en este primer capítulo no detalla los métodos ni evidencia empírica concreta.",

            # RESUMEN FINAL
            "Lattice: matriz universal, precursora del espacio-tiempo y la materia.",
            "Campo neuronal: distorsión de la Lattice creada por el cerebro, base de la percepción.",
            "Sintergia: índice de coherencia, densidad y frecuencia informacional que determina la calidad de interpretación.",
            "Percepción como construcción: nuestra experiencia del mundo emerge de la interacción entre el cerebro y la Lattice.",
            "Estado de Unidad: meta última, disolución del ego y fusión con el campo universal."
        ]
        self.logger.info("1. Creating audio script...")
        audio_path = generar_voz("".join(script),
                                 voz="es-MX-JorgeNeural",
                                 output_file="salida.mp3",
                                 output_subs="subtitles.srt")
        self.logger.info(f"Archivo MP3 generado en: {audio_path}")
        assert self.file_exists(audio_path), "Expecting MP3 to exist!"

        self.logger.info("2. Creating complete sized video based on MP3 lenght...")
        audio_len = len(AudioSegment.from_file(audio_path))//1000
        self.logger.info(f"Audio lenght in seconds: {audio_len}")

        self.logger.info(f"3. Creating video loop to fit audio len ({audio_len} seconds)...")
        video_template_repetition = math.ceil(audio_len/self.VIDEO_TEMPLATE_LEN)
        self.logger.info(f"Will join #{video_template_repetition} video_templates to fit {audio_len}")

        assert self.file_exists(self.VIDEO_TEMPLATE_PATH), "Unable to reach video_template!"
        video_list = [self.VIDEO_TEMPLATE_PATH]*video_template_repetition
        non_audio_video_join(*video_list, output_path="output_joined.mp4")

        self.logger.info("4. Joining video + audio track...")
        assert self.file_exists("output_joined.mp4"), "Video with no audio shall exist"
        output_video_path = video_audio_join(*["output_joined.mp4", audio_path])
        assert self.file_exists(output_video_path)
        
        self.logger.info("5. Joining video (with audio track) + subs")
        output_video_subs_path = video_join_subs(video_input_path=output_video_path,
                                                 subtitle_path="subtitles.srt",
                                                 output_path="video_with_subs.mp4")
        assert self.file_exists(output_video_subs_path), "Video + SRT shall exist!"

        self.logger.info("6. Joining video (with audio track) + music audio track (low volume)")
        output_video_with_music = merge_media(video_input=output_video_subs_path,
                                              audio_input=self.config["media_src"]["music_track"],
                                              volume_factor=0.2,
                                              outputfile="final_video_with_music.mp4")

        assert self.file_exists(output_video_with_music), "Final Video with Music shall exist!"
