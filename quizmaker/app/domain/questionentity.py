import uuid
import random
from typing import Tuple

from dataclasses import dataclass, field


@dataclass(frozen=True)
class QuestionEntity:
    answer: str
    description: str = ''
    has_variations: bool = field(default=False)
    # A unique reference within the quiz aggregate
    ref: str = field(default_factory=lambda: str(uuid.uuid4()))

    def as_dict(self):
        return {
            'answer': self.answer,
            'question': self.description,
            'has_variations': self.has_variations,
            'ref': self.ref
        }


@dataclass(frozen=True)
class MultipleChoiceQuestionEntity(QuestionEntity):
    pass


@dataclass(frozen=True)
class PictureQuestionEntity(QuestionEntity):
    pics: Tuple[str, ...] = field(default_factory=lambda: ())
    clue: str = ''

    def as_dict(self):
        return {
            'pics': None if len(self.pics) == 0 else self.pics,
            'clue': self.clue,
            **super().as_dict()
        }


@dataclass(frozen=True)
class VideoQuestionEntity(QuestionEntity):
    video: str = ''
    choices: Tuple[str, ...] = field(default_factory=lambda: ())

    @property
    def choices_list(self):
        choices = [*self.choices, self.answer]
        random.shuffle(choices)
        return choices

    def as_dict(self):
        return {
            'video': self.video,
            'choices': ', '.join(self.choices),
            'choices_as_list': self.choices,
            **super().as_dict()
        }
