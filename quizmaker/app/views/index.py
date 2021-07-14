from django.http import HttpResponse, Http404
from django.views.generic.list import ListView
from django.shortcuts import render
from django.conf import settings

from ..models import QuizModel
from ..services.quiz_repository import QuizRepository
from ..services.demo_seeder import demo_seeder_service


class PlayIndexview(ListView):
    model = QuizModel
    template_name = 'app/play_index.html'
    ordering = ['created_at']


def scoreboard(request):
    res = QuizRepository.get_high_scorers()
    return render(request, 'app/scoreboard.html', {'score_list': res})


def demo_seeder(request, key):
    master_key = settings.DEMO_SEEDER_KEY

    if master_key is None or len(master_key) < 12 or len(key) < 12 or master_key != key:
        raise Http404

    try:
        demo_seeder_service()
    except Exception:
        raise Http404

    return HttpResponse('Demo seed done.')
