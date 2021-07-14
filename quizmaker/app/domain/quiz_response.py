from dataclasses import dataclass
from typing import Dict
import uuid
import hashlib

from .questionentity import QuestionEntity
from .quizentity import QuizEntity


@dataclass
class QuestionResponseEntity:
    question_ref: str
    answer: str = ''
    is_correct: bool = False

    def mark_answer(self, question: QuestionEntity) -> None:
        if question.has_variations:
            answers = list(map(lambda a: str.strip(a).upper(), question.answer.split(",")))
            self.is_correct = self.answer.upper() in answers
        else:
            self.is_correct = question.answer.upper() == self.answer.upper()

    @property
    def has_answer(self):
        return len(self.answer.strip()) > 0


AnswersBucketType = Dict[str, QuestionResponseEntity]


class QuizResponseEntity:
    name: str = ''
    email: str = ''
    token: str = ''
    answers_bucket: AnswersBucketType = {}
    correct_items: int = 0
    score: float = 0.00
    _quiz: QuizEntity

    def __init__(self, quiz: QuizEntity, answers_bucket: AnswersBucketType, **kwargs):
        self._quiz = quiz
        self.answers_bucket = answers_bucket
        if kwargs.get('name') is not None:
            self.title = kwargs.get('name')
        if kwargs.get('title') is not None:
            self.description = kwargs.get('title')
        if kwargs.get('token') is not None:
            self.token = kwargs.get('token')
        else:
            self.token = hashlib.md5(uuid.uuid4().bytes).hexdigest()

    @staticmethod
    def create_response(quiz: QuizEntity, **kwargs):
        bucket = {}
        for q in quiz.questions:
            bucket[q.ref] = QuestionResponseEntity(question_ref=q.ref)
        return QuizResponseEntity(quiz=quiz, answers_bucket=bucket, **kwargs)

    def set_answers(self, answers: dict):
        for ref, ans in answers.items():
            if ref in self.answers_bucket:
                self.answers_bucket[ref].answer = str.strip(ans)

    def mark_quiz(self):
        self.correct_items = 0
        for q in self._quiz.questions:
            if q.ref in self.answers_bucket:
                resp = self.answers_bucket[q.ref]
                resp.mark_answer(q)
                self.correct_items += 1 if resp.is_correct else 0
        self.score = float(self.correct_items) / float(len(self.answers_bucket)) * 100

    @property
    def answers_as_list(self):
        ret = {}
        for k, i in self.answers_bucket.items():
            ret[i.question_ref] = {
                'ref': i.question_ref,
                'answer': i.answer,
                'is_correct': i.is_correct
            }
        return ret

    @property
    def quiz_snapshot(self):
        return self._quiz.as_dict()
