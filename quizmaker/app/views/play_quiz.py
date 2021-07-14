import logging
from django.forms import formset_factory
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View

from ..services.factory import QuizFactory
from ..services.form_handler import FORM_FATAL_ERROR_MSG
from .generic_form_view import QuizRepository
from ..forms.quiz import *
from ..models import *

logger = logging.getLogger(__name__)


class PlayQuizMixin:
    form = ResponseForm
    questions_form = None
    questions_form_prefix = 'ritem'
    template = ''
    quiz_type = ''
    _quiz = None
    _mquiz = None  # Model instance

    def _init_quiz_template(self, type):
        if type == 'multiple_choice':
            template = 'app/play.multiple-choice-quiz.html'
        elif type == 'picture':
            template = 'app/play.picture-quiz.html'
        elif type == 'video':
            template = 'app/play.video-quiz.html'
        else:
            raise Http404
        self.template = template

    def _init_quiz_factory(self):
        self.questions_form = formset_factory(
            ResponseItemForm,
            extra=0,
            min_num=len(self._quiz.questions),
            max_num=len(self._quiz.questions),
            validate_min=True,
            validate_max=True,
        )

    def _get_render_vars(self, questions_form):
        if self._quiz.type == 'multiple_choice':
            answers_list = self._quiz.get_answers_as_list()
            random.shuffle(answers_list)
            render_vars = {
                'answers_list': answers_list,
                'questions_list': zip(questions_form, self._quiz.questions),
            }
        else:
            render_vars = {
                'questions_list': zip(questions_form, self._quiz.questions),
            }
        return render_vars


class PlayQuizView(View, PlayQuizMixin):
    def get(self, request, quiz_id=None):
        self._init_quiz_model(quiz_id)
        form = self.form()
        questions_form = self.questions_form(prefix=self.questions_form_prefix)
        render_vars = self._get_render_vars(questions_form)
        return render(request, self.template, {
            'quiz_type': self._mquiz.type,
            'description': self._quiz.description,
            'title': self._quiz.title,
            'form': form,
            'questions_form': questions_form,
            **render_vars
        })

    def post(self, request, quiz_id=None):
        self._init_quiz_model(quiz_id)
        form = self.form(request.POST)
        questions_form = self.questions_form(request.POST, prefix=self.questions_form_prefix)
        valid_qforms = []

        if questions_form.is_valid():
            fvalid_qforms = list(filter(lambda x: len(x.cleaned_data) > 0, questions_form))
            valid_qforms = list(map(lambda x: x.cleaned_data, fvalid_qforms))

        if form.is_valid() and valid_qforms:
            try:
                resp = QuizFactory.build_quiz_response(self._quiz, form.cleaned_data, valid_qforms)
                mresp = QuizRepository.create_quiz_response(resp)
                return redirect('app:results_view', resp_id=mresp.id, token=mresp.token)
            except InvariantException as ie:
                logger.error(ie, exc_info=True)
                form.add_error(None, ie)
            except Exception as e:
                logger.error(e, exc_info=True)
                form.add_error(None, FORM_FATAL_ERROR_MSG)

        render_vars = self._get_render_vars(questions_form)

        return render(request, self.template, {
            'quiz_type': self._mquiz.type,
            'description': self._quiz.description,
            'title': self._quiz.title,
            'form': form,
            'questions_form': questions_form,
            **render_vars
        })

    def _init_quiz_model(self, quiz_id):
        mquiz = get_object_or_404(QuizModel, id=quiz_id)
        if mquiz.type == 'multiple_choice':
            quiz = QuizFactory.map_multiple_choice_model(mquiz)
        elif mquiz.type == 'picture':
            quiz = QuizFactory.map_picture_model(mquiz)
        elif mquiz.type == 'video':
            quiz = QuizFactory.map_video_model(mquiz)
        else:
            raise Http404
        self._mquiz = mquiz
        self._quiz = quiz
        self._init_quiz_factory()
        self._init_quiz_template(mquiz.type)


class QuizResponseView(PlayQuizMixin, View):
    def get(self, request, resp_id=None, token=None):
        resp = get_object_or_404(QuizResponseModel, id=resp_id, token=token)
        self._build_quiz_snapshot(resp.snapshot)
        form = self.form()
        questions_form = self.questions_form(prefix=self.questions_form_prefix)
        render_vars = self._get_render_vars(questions_form)
        return render(request, self.template, {
            'quiz_type': self._quiz.type,
            'description': self._quiz.description,
            'title': self._quiz.title,
            'form': form,
            'questions_form': questions_form,
            'results_view': True,
            'resp': resp,
            **render_vars
        })

    def _build_quiz_snapshot(self, snapshot):
        if snapshot.get('type') == 'multiple_choice':
            quiz = QuizFactory.build_multiple_choice_entity(snapshot, snapshot.get('questions'))
        elif snapshot.get('type') == 'picture':
            quiz = QuizFactory.build_picture_entity(snapshot, snapshot.get('questions'))
        elif snapshot.get('type') == 'video':
            quiz = QuizFactory.build_video_entity(snapshot, snapshot.get('questions'))
        else:
            raise Http404
        self._quiz = quiz
        self._init_quiz_factory()
        self._init_quiz_template(self._quiz.type)
