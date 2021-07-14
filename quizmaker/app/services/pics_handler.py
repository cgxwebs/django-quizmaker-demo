import os
import shutil
import uuid
import hashlib
import re
from typing import List

from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from PIL import Image

IMAGE_MAX_PIXELS = 400
UPLOAD_SUBDIR = settings.PIC_QUIZ_DIR


def unpack_form(form_data: dict, prefix: str) -> list:
    """ Unpacks a cleaned data to retrieve only images """
    regex = f'^{prefix}[0-9]+$'
    return [v for (k, v) in form_data.items() if re.match(regex, k)]


def upload_multiple(files: List[TemporaryUploadedFile]):
    uploaded = []
    for f in files:
        uploaded.append(upload_image(f))
    return uploaded


def upload_image(file: TemporaryUploadedFile):
    new_file_path = settings.MEDIA_ROOT
    file_name = UPLOAD_SUBDIR + '/' + hashlib.md5(uuid.uuid4().bytes).hexdigest()

    if file.content_type == 'image/jpeg':
        file_name += '.jpeg'
    elif file.content_type == 'image/png':
        file_name += '.png'
    else:
        raise Exception('Invalid file type')

    try:
        new_file_path = str(new_file_path) + '/' + str(file_name)
        shutil.move(file.temporary_file_path(), new_file_path)
        os.chmod(new_file_path, 0o644)
        resize_image(new_file_path)
    except Exception as e:
        if os.path.isfile(new_file_path):
            os.remove(new_file_path)
        raise e

    if not os.path.isfile(new_file_path):
        raise Exception('File was not processed successfully')

    return file_name


def resize_image(file_path):
    img = Image.open(file_path)
    width = img.size[0]
    height = img.size[1]

    if height <= IMAGE_MAX_PIXELS and width <= IMAGE_MAX_PIXELS:
        img.close()
        return None

    new_width, new_height = get_new_dimensions(width, height)
    resized = img.resize((new_width, new_height), Image.ANTIALIAS)
    resized.save(file_path, quality=90, compress_level=2, subsampling=0)
    resized.close()
    img.close()


def get_new_dimensions(width, height):
    if height > IMAGE_MAX_PIXELS:
        perc = IMAGE_MAX_PIXELS / float(height)
        new_height = IMAGE_MAX_PIXELS
        new_width = int((float(width) * float(perc)))
    elif width > IMAGE_MAX_PIXELS:
        perc = IMAGE_MAX_PIXELS / float(width)
        new_height = int((float(height) * float(perc)))
        new_width = IMAGE_MAX_PIXELS
    else:
        new_width = width
        new_height = height

    if height <= IMAGE_MAX_PIXELS and width <= IMAGE_MAX_PIXELS:
        return new_width, new_height
    else:
        return get_new_dimensions(new_width, new_height)
