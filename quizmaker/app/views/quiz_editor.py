import logging

from django.forms import formset_factory
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, render

from ..services.factory import QuizFactory
from ..services.pics_handler import unpack_form, upload_multiple
from ..services.form_handler import *
from .generic_form_view import GenericFormView, QuizRepository
from ..forms.quiz import *

logger = logging.getLogger(__name__)


class CreateViewMixin:
    def get(self, request):
        return self.perform_get(request)

    def post(self, request):
        return self.perform_post(request)


class EditViewMixin:
    def get(self, request, quiz_id, token):
        return self.perform_get(request, quiz_id, token)

    def post(self, request, quiz_id, token):
        return self.perform_post(request, quiz_id, token)

    def get_render_args(self, form, questions_forms) -> dict:
        return {
            'is_edit': True,
            'form': self.form(initial=self._form_initial_data),
            'questions_form': self.questions_form(prefix=self.questions_form_prefix,
                                                  initial=self._form_initial_data.get('questions'))
        }

    def post_render_args(self, form, questions_forms, valid_qforms) -> dict:
        return {
            'is_edit': True
        }


class MultipleChoiceConfigMixin:
    form = MultipleChoiceQuizForm
    entity = MultipleChoiceQuizEntity
    questions_form = formset_factory(MultipleChoiceQuestionForm, max_num=MultipleChoiceQuizEntity.MAX_NUM_QUESTIONS)
    questions_form_prefix = 'mcq'
    quiz_type = 'selection'
    quiz_description = 'Define a question and its answer on each row. Provide a dummy answer at the bottom.'


class MultipleChoiceCreateView(MultipleChoiceConfigMixin, CreateViewMixin, GenericFormView):
    def on_success(self, form_data, valid_qforms) -> HttpResponse:
        quiz = QuizFactory.build_multiple_choice_entity(form_data, valid_qforms)
        mquiz = QuizRepository.create_multiple_choice_quiz(quiz)
        messages.add_message(self._request, messages.SUCCESS, 'Your quiz has been created!')
        return redirect('app:edit_multi', quiz_id=mquiz.id, token=mquiz.edit_token)


class MultipleChoiceEditView(MultipleChoiceConfigMixin, EditViewMixin, GenericFormView):
    questions_form = formset_factory(MultipleChoiceQuestionForm, extra=0, max_num=MultipleChoiceQuizEntity.MAX_NUM_QUESTIONS)

    def on_success(self, form_data, valid_qforms) -> HttpResponse:
        updated_quiz = QuizFactory.build_multiple_choice_entity(form_data, valid_qforms)
        QuizRepository.update_multiple_choice_quiz(self._mquiz, updated_quiz)
        messages.add_message(self._request, messages.SUCCESS, 'Quiz has been saved.')
        return redirect('app:edit_multi', quiz_id=self._quiz.id, token=self._quiz.edit_token)


class PictureConfigMixin:
    form = PictureQuizForm
    entity = PictureQuizEntity
    questions_form = formset_factory(PictureQuestionForm, max_num=PictureQuizEntity.MAX_NUM_QUESTIONS)
    questions_form_prefix = 'pic'
    quiz_type = 'picture'
    quiz_description = 'Upload 4 photos that provide clues to the word to be guessed by the player. The word context may come in different variations separated by commas (i.e. dog, dogs, puppy, puppies). A separate text clue may also be provided.'


class PictureCreateView(PictureConfigMixin, CreateViewMixin, GenericFormView):
    def preprocess_forms(self, form, questions_form):
        questions_form = populate_pics(questions_form, self._request.FILES)
        return form, questions_form

    def on_success(self, form_data, valid_qforms) -> HttpResponse:
        for r in valid_qforms:
            uploaded = upload_multiple(unpack_form(r, 'pic'))
            r['uploaded'] = uploaded
        quiz = QuizFactory.build_picture_entity(form_data, valid_qforms)
        mquiz = QuizRepository.create_picture_quiz(quiz)
        messages.add_message(self._request, messages.SUCCESS, 'Your quiz has been created!')
        return redirect('app:edit_picture', quiz_id=mquiz.id, token=mquiz.edit_token)


class PictureEditView(PictureConfigMixin, EditViewMixin, GenericFormView):
    questions_form = formset_factory(PictureQuestionForm, extra=0, max_num=PictureQuizEntity.MAX_NUM_QUESTIONS)

    def preprocess_forms(self, form, questions_form):
        questions_form = populate_pics(questions_form, self._request.FILES)
        return form, questions_form

    def on_success(self, form_data, valid_qforms) -> HttpResponse:
        pics_by_ref = self._get_pics_by_ref()
        for i in valid_qforms:
            if i.get('pics') is None:
                i['uploaded'] = pics_by_ref[i.get('ref')]
            else:
                i['uploaded'] = upload_multiple(unpack_form(i, 'pic'))
        updated_quiz = QuizFactory.build_picture_entity(form_data, valid_qforms)
        QuizRepository.update_picture_quiz(self._mquiz, updated_quiz)
        messages.add_message(self._request, messages.SUCCESS, 'Quiz has been saved.')
        return redirect('app:edit_picture', quiz_id=self._quiz.id, token=self._quiz.edit_token)

    def get_render_args(self, form, questions_forms) -> dict:
        return {
            'pics_by_ref': self._get_pics_by_ref(),
            **super().get_render_args(form, questions_forms)
        }

    def post_render_args(self, form, questions_forms, valid_qforms) -> dict:
        return {
            'pics_by_ref': self._get_pics_by_ref(),
            **super().post_render_args(form, questions_forms, valid_qforms)
        }

    def _get_pics_by_ref(self):
        pics_by_ref = {}
        for q in self._quiz.questions:
            pics_by_ref[str(q.ref)] = q.pics
        return pics_by_ref


class VideoConfigMixin:
    form = VideoQuizForm
    entity = VideoQuizEntity
    questions_form = formset_factory(VideoQuestionForm, max_num=VideoQuizEntity.MAX_NUM_QUESTIONS)
    questions_form_prefix = 'vid'
    quiz_type = 'video'
    quiz_description = 'Provide a Youtube video ID, a question, dummy choices, and the correct answer for each row. The dummy choices must exactly be 3, separated by commas.'


class VideoCreateView(VideoConfigMixin, CreateViewMixin, GenericFormView):
    def on_success(self, form_data, valid_qforms) -> HttpResponse:
        quiz = QuizFactory.build_video_entity(form_data, valid_qforms)
        mquiz = QuizRepository.create_video_quiz(quiz)
        messages.add_message(self._request, messages.SUCCESS, 'Your quiz has been created!')
        return redirect('app:edit_video', quiz_id=mquiz.id, token=mquiz.edit_token)


class VideoEditView(VideoConfigMixin, EditViewMixin, GenericFormView):
    questions_form = formset_factory(VideoQuestionForm, extra=0, max_num=VideoQuizEntity.MAX_NUM_QUESTIONS)

    def on_success(self, form_data, valid_qforms) -> HttpResponse:
        updated_quiz = QuizFactory.build_video_entity(form_data, valid_qforms)
        QuizRepository.update_video_quiz(self._mquiz, updated_quiz)
        messages.add_message(self._request, messages.SUCCESS, 'Quiz has been saved.')
        return redirect('app:edit_video', quiz_id=self._quiz.id, token=self._quiz.edit_token)


def index(request):
    return render(request, 'app/create.quiz.html')
