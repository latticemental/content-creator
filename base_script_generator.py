from .base_content_creator import BaseContentCreatorHorizontal, BaseContentCreatorVertical


class BaseContentScriptAIGenerator:
    """
    BaseContentScriptAIGenerator
    """

    def _generate_script_by_prompt(self, prompt: str) -> str:
        """
        Generate script by prompt using OpenAI API
        """
        pass

    def generate_longform_script(self, TBD: str) -> str:
        """
        Generate Longform video script
        """
        return self._generate_script_by_prompt(TBD)

    def generate_shortform_script(self, TBD: str) -> str:
        """
        Generate Shortform video script
        """
        return self._generate_script_by_prompt(TBD)
