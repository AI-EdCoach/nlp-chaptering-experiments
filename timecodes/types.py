from dataclasses import dataclass
from typing import List


@dataclass
class Chapter:
    """
    A single chapter of text.
    """

    start: int
    end: int
    content: str
    title: str = None

    def __post_init__(self):
        self.start = int(self.start)
        self.end = int(self.end)
        if self.title is None:
            self.title = " ".join(self.content.split(" ")[:5]) + "..."

@dataclass
class Timecodes:
    """
    A list of chapters of transcript from media file.
    """
    chapters: List[Chapter]
    media_file: str

    def __str__(self):
        return "\n".join([self.media_file]
                         + [f"{chapter.start} {chapter.title}" for chapter in self.chapters])