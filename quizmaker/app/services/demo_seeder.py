import json
import random
import uuid
import hashlib
import os
import shutil

from django.db import connection
from django.conf import settings

from ..models import QuizResponseModel
from ..services.factory import QuizFactory
from ..services.quiz_repository import QuizRepository


def demo_seeder_service():
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE app_quiz CASCADE; TRUNCATE app_quizresponse;")

    file = open(settings.BASE_DIR / 'app/demo_data.json', 'r')
    cont = file.read()
    file.close()
    json_cont = json.loads(cont)

    rand_quiz = random.sample(json_cont['quiz'], len(json_cont['quiz']))
    for dat in rand_quiz:
        if dat['type'] == 'multiple_choice':
            entity = QuizFactory.build_multiple_choice_entity(dat, dat['questions'])
            QuizRepository.create_multiple_choice_quiz(entity)
        elif dat['type'] == 'picture':
            entity = QuizFactory.build_picture_entity(dat, dat['questions'])
            QuizRepository.create_picture_quiz(entity)
        else:
            entity = QuizFactory.build_video_entity(dat, dat['questions'])
            QuizRepository.create_video_quiz(entity)

    for dat in json_cont['responses']:
        dat['score'] = random.random() * 100.00
        dat['correct_items'] = random.randint(0, 50)
        dat['token'] = hashlib.md5(uuid.uuid4().bytes).hexdigest()
        model = QuizResponseModel(**dat)
        model.save()

    media_dir = str(settings.MEDIA_ROOT) + settings.PIC_QUIZ_DIR
    if os.path.isdir(media_dir):
        shutil.rmtree(media_dir)
        os.mkdir(media_dir)

    return True
