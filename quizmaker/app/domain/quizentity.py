from typing import Tuple, List
from abc import ABC, abstractmethod
import uuid
import hashlib

from .questionentity import *
from .exceptions import InvariantException

QuestionTuple = Tuple[QuestionEntity, ...]


class QuizEntity(ABC):
    REQUIRED_NUM_QUESTIONS = 1
    MAX_NUM_QUESTIONS = 10
    id: int = 0
    title: str = ''
    description: str = ''
    type: str = ''
    _questions: QuestionTuple = ()
    edit_token: str = ''

    def __init__(self, **kwargs):
        if kwargs.get('title') is not None:
            self.title = kwargs.get('title')
        if kwargs.get('description') is not None:
            self.description = kwargs.get('description')
        if kwargs.get('edit_token') is not None:
            self.edit_token = kwargs.get('edit_token')
        else:
            self.edit_token = hashlib.md5(uuid.uuid4().bytes).hexdigest()

    def as_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'questions': [q.as_dict() for q in self._questions]
        }

    @property
    def questions(self) -> QuestionTuple:
        return self._questions

    @staticmethod
    @abstractmethod
    def make_question(*args, **kwargs) -> QuestionEntity:
        pass


class MultipleChoiceQuizEntity(QuizEntity):
    REQUIRED_NUM_QUESTIONS = 3
    MAX_NUM_QUESTIONS = 20
    dummy_answer: str
    type = 'multiple_choice'

    def __init__(self, questions: QuestionTuple, dummy_answer: str, **kwargs):
        if self.REQUIRED_NUM_QUESTIONS > len(questions) < self.MAX_NUM_QUESTIONS:
            raise InvariantException('Required number of questions not met')
        self._questions = questions
        self.dummy_answer = dummy_answer
        super().__init__(**kwargs)

    @staticmethod
    def make_question(question: str, answer: str, ref: str = None) -> QuestionEntity:
        if ref is None:
            return MultipleChoiceQuestionEntity(description=question, answer=answer)
        return MultipleChoiceQuestionEntity(description=question, answer=answer, ref=ref)

    def get_answers_as_list(self):
        answers = []
        for q in self.questions:
            answers.append(q.answer)
        answers.append(self.dummy_answer)
        return answers

    def as_dict(self):
        return {
            'dummy_answer': self.dummy_answer,
            **super().as_dict()
        }


class PictureQuizEntity(QuizEntity):
    MAX_NUM_QUESTIONS = 10
    type = 'picture'

    def __init__(self, questions: QuestionTuple, **kwargs):
        if self.REQUIRED_NUM_QUESTIONS > len(questions) < self.MAX_NUM_QUESTIONS:
            raise InvariantException('Required number of questions not met')
        self._questions = questions
        super().__init__(**kwargs)

    @staticmethod
    def make_question(pics: Tuple[str, ...], answer: str, clue: str = '', ref: str = None) -> QuestionEntity:
        if len(pics) != 4:
            raise InvariantException('Required number of pictures not met')
        args = {
            'pics': tuple(pics),
            'clue': clue,
            'answer': answer,
            'has_variations': True
        }
        if ref is not None:
            args['ref'] = ref
        return PictureQuestionEntity(**args)


class VideoQuizEntity(QuizEntity):
    MAX_NUM_QUESTIONS = 10
    type = 'video'

    def __init__(self, questions: QuestionTuple, **kwargs):
        if self.REQUIRED_NUM_QUESTIONS > len(questions) < self.MAX_NUM_QUESTIONS:
            raise InvariantException('Required number of questions not met')
        self._questions = questions
        super().__init__(**kwargs)

    @staticmethod
    def make_question(question: str, video: str, answer: str, choices: Tuple[str,...], ref: str = None) -> QuestionEntity:
        if len(choices) != 3:
            raise InvariantException('Choices must exactly be 3 items.')
        args = {
            'description': question,
            'video': video,
            'choices': choices,
            'answer': answer,
            'has_variations': False
        }
        if ref is not None:
            args['ref'] = ref
        return VideoQuestionEntity(**args)


