from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index.PlayIndexview.as_view(), name='play_index'),
    path('scoreboard/', views.index.scoreboard, name='scoreboard'),
    path('create/', views.quiz_editor.index, name='create_index'),
    path('create/selection/', views.quiz_editor.MultipleChoiceCreateView.as_view(), name='create_multi'),
    path('edit/selection/<int:quiz_id>/<str:token>', views.quiz_editor.MultipleChoiceEditView.as_view(), name='edit_multi'),
    path('create/picture/', views.quiz_editor.PictureCreateView.as_view(), name='create_picture'),
    path('edit/picture/<int:quiz_id>/<str:token>', views.quiz_editor.PictureEditView.as_view(), name='edit_picture'),
    path('create/video/', views.quiz_editor.VideoCreateView.as_view(), name='create_video'),
    path('edit/video/<int:quiz_id>/<str:token>', views.quiz_editor.VideoEditView.as_view(), name='edit_video'),
    path('play/<int:quiz_id>', views.play_quiz.PlayQuizView.as_view(), name='play_view'),
    path('results/<int:resp_id>/<str:token>', views.play_quiz.QuizResponseView.as_view(), name='results_view'),
    path('demo-seeder/<str:key>', views.index.demo_seeder, name='demo_seeder'),
]
