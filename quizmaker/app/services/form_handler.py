import logging

from ..domain.exceptions import InvariantException

FORM_FATAL_ERROR_MSG = 'Oops... Cannot process form right now.'
MAX_PICS_PER_ROW = 4
logger = logging.getLogger(__name__)


def get_clean_data_from_set(setform):
    fvalid = list(filter(lambda x: len(x.cleaned_data) > 0, setform))
    valid = list(map(lambda x: x.cleaned_data, fvalid))
    return valid


def populate_pics(questions_form: list, files: dict):
    row = 0
    for key in files:
        pics = files.getlist(key)
        found_row = False
        while not found_row and row < len(questions_form):
            found_row = questions_form[row]['pics'].data is not None
            row += 1 if not found_row else 0
        if found_row:
            for ctr in range(min(len(pics), MAX_PICS_PER_ROW)):
                field_name = f'pic{ctr + 1}'
                questions_form[row].fields[field_name].initial = pics[ctr]
            row += 1
    return questions_form
