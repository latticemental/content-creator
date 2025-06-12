from .base_content_creator import BaseContentCreatorHorizontal, BaseContentCreatorVertical
from enum import Enum


class ContentType(Enum):
    AUDIOBOOK = "audiobook"
    GENERAL_TOPIC = "general_topic"


class BaseContentScriptAIGenerator:
    """
    BaseContentScriptAIGenerator
    """

    def _generate_script_by_prompt(self, prompt: str) -> str:
        """
        Generate script by prompt using OpenAI API
        """
        pass

    def _get_audiobook_by_chapter_prompt(self, book: str, author: str, chapter: int, duration: int) -> list:
        """
        Retrieve OpenAI prompt for audiobook from a specific chapter

        Params:
            author: str, book author
            chapter: int, book chapter to analyze
            duration: int, expected duration in seconds
        """
        prompt = (
            f"Eres un narrador claro y cautivador. Resume el capítulo {chapter} del libro '{book}' de {author} "
            f"en forma de guion narrativo. El resumen debe incluir los conceptos clave, ideas centrales y tono espiritual o científico "
            f"según lo presenta el autor. Divide el guion en partes (inicio, desarrollo, cierre) y escribe en un lenguaje accesible para una audiencia general, "
            f"manteniendo el estilo reflexivo característico de {author}. El texto debe estar pensado para ser narrado en voz alta en aproximadamente "
            f"{duration} segundos. No inventes información, y si algo no está claro en el capítulo, menciónalo."
        )
        return [
            {"role": "system", "content": "Eres un escritor profesional de guiones narrativos."},
            {"role": "user", "content": prompt}
        ]

    def _get_audiobook_complete_prompt(self, book: str, author: str, duration: int) -> list:
        """
        Retrieve OpenAI prompt for a complete audiobook
        """
        prompt = (
            f"Eres un narrador claro y cautivador. Resume el libro completo '{book}' de {author} "
            f"en forma de guion narrativo. El resumen debe incluir los conceptos clave, ideas centrales y tono espiritual o científico "
            f"según lo presenta el autor. Divide el guion en partes (inicio, desarrollo, cierre) y escribe en un lenguaje accesible para una audiencia general, "
            f"manteniendo el estilo reflexivo característico de {author}. El texto debe estar pensado para ser narrado en voz alta en aproximadamente "
            f"{duration} segundos. No inventes información, y si algo no está claro en el capítulo, menciónalo."
        )
        return [
            {"role": "system", "content": "Eres un escritor profesional de guiones narrativos."},
            {"role": "user", "content": prompt}
        ]

    def _get_topic_prompt(self, topic, **kwargs):
        """
        Retrieved OpenAI prompt for a given topic
        """

    def generate_longform_script(self, content_type: ContentType) -> str:
        """
        Generate Longform video script
        """
        return self._generate_script_by_prompt(content_type)

    def generate_shortform_script(self, content_type: ContentType) -> str:
        """
        Generate Shortform video script
        """
        return self._generate_script_by_prompt(content_type)
