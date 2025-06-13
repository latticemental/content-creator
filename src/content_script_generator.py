from enum import Enum
from dotenv import load_dotenv
from abc import ABC, abstractmethod
import requests
import os
import json
import logging

load_dotenv() # Load .env for API Keys - Potentially, move to another place


class ContentScriptType(Enum):
    AUDIOBOOK = "audiobook"
    AUDIOBOOK_CHAPTER = "audiobook_chapter"
    GENERAL_TOPIC = "general_topic"


class ContentScriptGenerator(ABC):
    """
    ContentScriptGenerator
    """

    HEADER = "Eres un escritor profesional de guiones narrativos."
    FOOTER = ("Importante: No incluyas ninguna introducción ni explicación fuera del guion ni indicadores como Inicio, desarrollo, cierre o pausas. "
              "Devuelve únicamente el texto del guion que será leído por Text-to-Speech, sin comentarios previos ni posteriores. "
              "Si hay elementos poco claros en el capítulo, menciónalos dentro del guion mismo como reflexión del narrador, no como aclaración externa.")

    API_KEY: str
    API_URL: str

    def __init__(self):
        """
        Init ContentScriptGenerator
        """
        self.logger = logging.getLogger()

    @abstractmethod
    def _query(self, prompt: str) -> str:
        """Execute AI API query"""
    
    def get_audiobook_by_chapter(self, book: str, author: str, chapter: int, duration: int) -> str:
        """
        Retrieve AI Generated Script for a specific chapter of audiobook

        Params:
            book: str, book name
            author: str, book author
            chapter: int, book chapter to analyze
            duration: int, expected duration in seconds
        """
        prompt = (f"Resume el capítulo {chapter} del libro '{book}' de {author} en forma de guion narrativo, pensado para ser narrado en voz alta en aproximadamente {duration} segundos. " 
                  f"El resumen debe incluir los conceptos clave, ideas centrales y tono espiritual o científico según lo presenta el autor. " 
                  f"Divide el guion en partes (inicio, desarrollo, cierre) y escribe en un lenguaje accesible para una audiencia general, " 
                  f"manteniendo el estilo reflexivo característico de {author}. ")

        return self._query(prompt)

    def get_audiobook_complete(self, book: str, author: str, duration: int) -> list:
        """
        Retrieve AI Generated Script for a complete audiobook

        Params:
            book: str, book name
            author: str, book author
            duration: int, expected duration in seconds
        """
        prompt = (
            f"Eres un narrador claro y cautivador. Resume el libro completo '{book}' de {author} "
            f"en forma de guion narrativo. El resumen debe incluir los conceptos clave, ideas centrales y tono espiritual o científico "
            f"según lo presenta el autor. Divide el guion en partes (inicio, desarrollo, cierre) y escribe en un lenguaje accesible para una audiencia general, "
            f"manteniendo el estilo reflexivo característico de {author}. El texto debe estar pensado para ser narrado en voz alta en aproximadamente "
            f"{duration} segundos. No inventes información, y si algo no está claro en el capítulo, menciónalo. "
        )
        return self._query(prompt)

    def get_tales_content(self, topic: str) -> str:
        """
        Retrieve AI Generated Script for a storytelling
        """
        prompt = f"To be defined - {topic}"
        return self._query(prompt)

    def get_insight_content(self, topic: str) -> str:
        """
        Retrieve AI Generated Script for a topic Insight
        """
        prompt = f"To be defined - {topic}"
        return self._query(prompt)

    def get_misc_content(self, topic: str):
        """
        Retrieve AI Generated Script for a Miscelaneous topic
        """
        prompt = f"To be defined - {topic}"
        return self._query(prompt)


class ContentScriptGenerator_GeminiAI(ContentScriptGenerator):
    API_KEY = os.getenv("GEMINI_API_KEY")
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    def _query(self, prompt: str) -> str:
        """
        Execute AI Query using Gemini AI API
        """
        headers = {"Content-Type": "application/json"}

        data = {"contents": [{"parts": [{"text":f"{prompt}"}]}]}
        response = requests.post(self.API_URL,
                                 headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            result = response.json()
            self.logger.info(json.dumps(result, indent=2))
            return result["candidates"][0]["content"]["parts"][0]["text"].replace("**", "").replace("\n", "")
        else:
            self.logger.error(f"Error {response.status_code}: {response.text}")


class ContentScriptGenerator_OpenAI(ContentScriptGenerator):

    API_KEY = os.getenv("OPENAI_API_KEY")
    API_URL = "TO BE DEFINED"

    def _query(self, prompt: str) -> str:
        """
        Execute AI Query using OpenAI API
        """


def get_script_generator(engine: str) -> ContentScriptGenerator:
    """
    Retrieve Object for AI Content Script Generator
    """
    if engine == "gemini":
        return ContentScriptGenerator_GeminiAI()

    if engine == "openai":
        return ContentScriptGenerator_OpenAI()

    raise NotImplementedError(f"'{engine}' not supported.")
    