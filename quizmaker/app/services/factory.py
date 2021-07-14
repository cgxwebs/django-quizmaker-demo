from typing import Dict, List
from collections import ChainMap

from ..domain.quizentity import *
from ..domain.quiz_response import *
from ..models import *


class QuizFactory:

    @staticmethod
    def build_multiple_choice_entity(form_data: Dict, questions_data: List[Dict]) -> MultipleChoiceQuizEntity:
        questions = []
        for q in questions_data:
            questions.append(MultipleChoiceQuizEntity.make_question(
                question=q.get('question'),
                answer=q.get('answer'),
                ref=None if 'ref' not in q else q.get('ref')
            ))
        return MultipleChoiceQuizEntity(
            title=form_data.get('title'),
            description=form_data.get('description'),
            questions=tuple(questions),
            dummy_answer=form_data.get('dummy_answer')
        )

    @staticmethod
    def map_multiple_choice_model(model: QuizModel) -> MultipleChoiceQuizEntity:
        questions = []
        for q in model.questions.all():
            questions.append(MultipleChoiceQuizEntity.make_question(
                question=q.description,
                answer=q.answer,
                ref=q.id
            ))
        entity = MultipleChoiceQuizEntity(
            title=model.label,
            description=model.description,
            questions=tuple(questions),
            dummy_answer=model.extras.get('dummy_answer')
        )
        entity.id = model.id
        entity.edit_token = model.edit_token
        return entity

    @staticmethod
    def build_picture_entity(form_data: Dict, questions_data: List[Dict]) -> PictureQuizEntity:
        questions = []
        for q in questions_data:
            questions.append(PictureQuizEntity.make_question(
                pics=tuple(q.get('uploaded') if 'uploaded' in q else q.get('pics')),
                answer=q.get('answer'),
                clue=q.get('clue'),
                ref=None if 'ref' not in q else q.get('ref')
            ))
        return PictureQuizEntity(
            title=form_data.get('title'),
            description=form_data.get('description'),
            questions=tuple(questions),
        )

    @staticmethod
    def map_picture_model(model: QuizModel) -> PictureQuizEntity:
        questions = []
        for q in model.questions.all():
            questions.append(PictureQuizEntity.make_question(
                pics=tuple(q.extras.get('pics')),
                answer=q.answer,
                clue=q.extras.get('clue'),
                ref=q.id
            ))
        entity = PictureQuizEntity(
            title=model.label,
            description=model.description,
            questions=tuple(questions),
        )
        entity.id = model.id
        entity.edit_token = model.edit_token
        return entity

    @staticmethod
    def build_video_entity(form_data: Dict, questions_data: List[Dict]) -> VideoQuizEntity:
        questions = []
        for q in questions_data:
            choices = tuple(map(lambda x: str.strip(x), str(q.get('choices')).split(',')))
            questions.append(VideoQuizEntity.make_question(
                question=q.get('question'),
                video=q.get('video'),
                answer=q.get('answer'),
                choices=tuple(choices),
                ref=None if 'ref' not in q else q.get('ref')
            ))
        return VideoQuizEntity(
            title=form_data.get('title'),
            description=form_data.get('description'),
            questions=tuple(questions),
        )

    @staticmethod
    def map_video_model(model: QuizModel) -> VideoQuizEntity:
        questions = []
        for q in model.questions.all():
            questions.append(VideoQuizEntity.make_question(
                question=q.description,
                video=q.extras.get('video'),
                answer=q.answer,
                choices=q.extras.get('choices'),
                ref=q.id
            ))
        entity = VideoQuizEntity(
            title=model.label,
            description=model.description,
            questions=tuple(questions),
        )
        entity.id = model.id
        entity.edit_token = model.edit_token
        return entity

    @staticmethod
    def build_quiz_response(quiz_entity, form_data: Dict, questions_data: List[Dict]) -> QuizResponseEntity:
        refs = list(map(lambda x: {x['ref']: x['answer']}, questions_data))
        resp = QuizResponseEntity.create_response(quiz_entity)
        resp.name = form_data['name']
        resp.email = form_data['email']
        resp.set_answers(ChainMap(*refs))
        resp.mark_quiz()
        return resp

