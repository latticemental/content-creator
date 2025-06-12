from .base_content_creator import BaseContentCreatorHorizontal, BaseContentCreatorVertical
from .base_script_generator import BaseContentScriptAIGenerator
from pathlib import Path

class ContentGenerator_LongFormVideo(BaseContentCreatorHorizontal):
    """
    ContentGenerator_LongFormVideo
    """
    DEFAULT_LONGFORM_DURATION: int = 300
    DEFAULT_SPLIT_BY_CHAPTER: bool = True
    
    def __init__(self, output_path: Path):
        """
        ContentGenerator_LongFormVideo
        """
        self.script_generator = BaseContentScriptAIGenerator()

    def create_audiobook(self, author: str,
                         split_by_chapter: bool = DEFAULT_SPLIT_BY_CHAPTER,
                         duration_s: int = DEFAULT_LONGFORM_DURATION):
        """
        Create audiobook from a given template
        """

    def create_by_topic(self, topic: str, **kwargs):
        """
        Create longform video from a given topic + kwargs
        """

class ContentGenerator_ShortFormVideo(BaseContentCreatorVertical):
    """
    ContentGenerator_LongFormVideo
    """
