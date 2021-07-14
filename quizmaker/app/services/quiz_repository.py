from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from ..domain.quizentity import *
from ..domain.quiz_response import *
from ..models import *
from ..services import factory


class QuizRepository:

    @staticmethod
    def create_multiple_choice_quiz(entity: MultipleChoiceQuizEntity) -> QuizModel:
        mquiz = QuizModel(
            label=entity.title,
            description=entity.description,
            type=entity.type,
            extras={
                'dummy_answer': entity.dummy_answer
            },
            edit_token=entity.edit_token
        )
        mquiz.save()

        for q in entity.questions:
            mquiz.questions.create(
                quiz=mquiz,
                description=q.description,
                answer=q.answer,
                has_variations=q.has_variations
            )
        return mquiz

    @staticmethod
    def update_multiple_choice_quiz(mquiz: QuizModel, entity: MultipleChoiceQuizEntity) -> QuizModel:
        mquiz.label = entity.title
        mquiz.description = entity.description
        mquiz.extras = {
            'dummy_answer': entity.dummy_answer
        }
        mquiz.save()
        QuizQuestionModel.objects.filter(quiz=mquiz).delete()
        for q in entity.questions:
            mquiz.questions.create(
                quiz=mquiz,
                description=q.description,
                answer=q.answer,
                has_variations=q.has_variations
            )
        return mquiz

    @staticmethod
    def create_picture_quiz(entity: PictureQuizEntity) -> QuizModel:
        mquiz = QuizModel(
            label=entity.title,
            description=entity.description,
            type=entity.type,
            edit_token=entity.edit_token
        )
        mquiz.save()

        for q in entity.questions:
            mquiz.questions.create(
                quiz=mquiz,
                extras={
                    'pics': q.pics,
                    'clue': q.clue,
                },
                answer=q.answer,
                has_variations=q.has_variations,
            )
        return mquiz

    @staticmethod
    def update_picture_quiz(mquiz: QuizModel, entity: PictureQuizEntity) -> QuizModel:
        mquiz.label = entity.title
        mquiz.description = entity.description
        mquiz.save()
        QuizQuestionModel.objects.filter(quiz=mquiz).delete()
        for q in entity.questions:
            mquiz.questions.create(
                quiz=mquiz,
                extras={
                    'pics': q.pics,
                    'clue': q.clue,
                },
                answer=q.answer,
                has_variations=q.has_variations,
            )
        return mquiz

    @staticmethod
    def create_video_quiz(entity: VideoQuizEntity) -> QuizModel:
        mquiz = QuizModel(
            label=entity.title,
            description=entity.description,
            type=entity.type,
            edit_token=entity.edit_token
        )
        mquiz.save()

        for q in entity.questions:
            mquiz.questions.create(
                quiz=mquiz,
                description=q.description,
                extras={
                    'video': q.video,
                    'choices': q.choices,
                },
                answer=q.answer,
                has_variations=q.has_variations,
            )
        return mquiz

    @staticmethod
    def update_video_quiz(mquiz: QuizModel, entity: VideoQuizEntity) -> QuizModel:
        mquiz.label = entity.title
        mquiz.description = entity.description
        mquiz.save()
        QuizQuestionModel.objects.filter(quiz=mquiz).delete()
        for q in entity.questions:
            mquiz.questions.create(
                quiz=mquiz,
                description=q.description,
                extras={
                    'video': q.video,
                    'choices': q.choices,
                },
                answer=q.answer,
                has_variations=q.has_variations,
            )
        return mquiz

    @staticmethod
    def get_quiz_with_token(quiz_id: int, token: str, entity_class):
        queryset = QuizModel.objects.filter(id=quiz_id, edit_token=token).all()
        if len(queryset) == 1:
            quiz = queryset[0]
            if entity_class is MultipleChoiceQuizEntity:
                return factory.QuizFactory.map_multiple_choice_model(quiz), quiz
            elif entity_class is PictureQuizEntity:
                return factory.QuizFactory.map_picture_model(quiz), quiz
            elif entity_class is VideoQuizEntity:
                return factory.QuizFactory.map_video_model(quiz), quiz

        raise ObjectDoesNotExist()

    @staticmethod
    def create_quiz_response(entity: QuizResponseEntity) -> QuizResponseModel:
        mresp = QuizResponseModel(
            name=entity.name,
            email=entity.email,
            token=entity.token,
            answers=entity.answers_as_list,
            snapshot=entity.quiz_snapshot,
            score=entity.score,
            correct_items=entity.correct_items
        )
        mresp.save()
        return mresp

    @staticmethod
    def get_high_scorers():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT lower(name) as name, sum(correct_items) as total_correct_items, avg(score) as avg_score
                FROM app_quizresponse 
                GROUP BY lower(name), lower(email) 
                HAVING sum(correct_items) > 0
                ORDER BY total_correct_items DESC, avg_score DESC
                LIMIT 20;
            """)
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
