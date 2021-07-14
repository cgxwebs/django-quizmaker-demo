import logging

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, Http404

from ..domain.exceptions import InvariantException
from ..services.quiz_repository import QuizRepository
from ..services.form_handler import get_clean_data_from_set, FORM_FATAL_ERROR_MSG

logger = logging.getLogger(__name__)


class GenericFormView(View):
    form = None
    entity = None
    questions_form = None
    questions_form_prefix = ''
    editor_template = 'app/quiz_editor.html'
    quiz_type = ''
    quiz_description = ''
    _request = None
    _form_initial_data = {}
    _quiz = None
    _mquiz = None  # Model instance

    def init_forms(self, quiz_id=None, token=None):
        if quiz_id is not None and token is not None:
            try:
                self._quiz, self._mquiz = QuizRepository.get_quiz_with_token(quiz_id, token, self.entity)
                self._form_initial_data = self._quiz.as_dict()
            except Exception as e:
                logger.error(e, exc_info=True)
                raise Http404

    def perform_get(self, request, quiz_id=None, token=None):
        self._request = request
        form = self.form()
        questions_form = self.questions_form(prefix=self.questions_form_prefix)
        self.init_forms(quiz_id, token)
        return render(request, self.editor_template, {
            'quiz_type': self.quiz_type,
            'quiz_description': self.quiz_description,
            'form': form,
            'questions_form': questions_form,
            'edit_mode': self.questions_form_prefix,
            'rows_min': self.entity.REQUIRED_NUM_QUESTIONS,
            'rows_max': self.entity.MAX_NUM_QUESTIONS,
            **self.get_render_args(form, questions_form)
        })

    def perform_post(self, request, quiz_id=None, token=None):
        self._request = request
        form = self.form(request.POST)
        questions_form = self.questions_form(request.POST, prefix=self.questions_form_prefix, files=request.FILES)
        valid_qforms = []

        # Hook to modify forms before validation
        form, questions_form = self.preprocess_forms(form, questions_form)
        self.init_forms(quiz_id, token)

        if questions_form.is_valid():
            valid_qforms = get_clean_data_from_set(questions_form)
            self.validate_questions_form(form, valid_qforms)

        if form.is_valid() and valid_qforms:
            try:
                return self.on_success(form.cleaned_data, valid_qforms)
            except InvariantException as ie:
                logger.error(ie, exc_info=True)
                form.add_error(None, ie)
            except Exception as e:
                logger.error(e, exc_info=True)
                form.add_error(None, FORM_FATAL_ERROR_MSG)

        return render(request, self.editor_template, {
            'quiz_type': self.quiz_type,
            'quiz_description': self.quiz_description,
            'form': form,
            'questions_form': questions_form,
            'edit_mode': self.questions_form_prefix,
            'rows_min': self.entity.REQUIRED_NUM_QUESTIONS,
            'rows_max': self.entity.MAX_NUM_QUESTIONS,
            **self.post_render_args(form, questions_form, valid_qforms)
        })

    def preprocess_forms(self, form, questions_form):
        return form, questions_form

    def validate_questions_form(self, form, valid_qforms):
        errors = form.validate_questions_form(valid_qforms)
        for e in errors:
            form.add_error(None, e)

    def on_success(self, form_data, valid_qforms) -> HttpResponse:
        pass

    def get_render_args(self, form, questions_forms) -> dict:
        return {}

    def post_render_args(self, form, questions_forms, valid_qforms) -> dict:
        return {}


