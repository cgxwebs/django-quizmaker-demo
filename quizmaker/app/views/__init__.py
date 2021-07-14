from django.shortcuts import render

from . import index
from . import quiz_editor
from . import play_quiz


def handler404(request, exception):
    return render(request, 'app/error404.html')
