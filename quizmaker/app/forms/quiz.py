from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from ..domain.quizentity import *


class QuizQuestionsValidator:
    quiz_model = None

    def validate_questions_form(self, valid_qforms):
        if len(valid_qforms) < self.quiz_model.REQUIRED_NUM_QUESTIONS:
            return ['Minimum of ' + str(self.quiz_model.REQUIRED_NUM_QUESTIONS) + ' question']
        elif len(valid_qforms) > self.quiz_model.MAX_NUM_QUESTIONS:
            return ['Maximum of ' + str(self.quiz_model.MAX_NUM_QUESTIONS) + ' questions']
        return []


class MultipleChoiceQuizForm(forms.Form, QuizQuestionsValidator):
    quiz_model = MultipleChoiceQuizEntity
    title = forms.CharField(
        required=True,
        max_length=255,
        min_length=10,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )
    dummy_answer = forms.CharField(
        required=True,
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )


class MultipleChoiceQuestionForm(forms.Form):
    question = forms.CharField(
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )
    answer = forms.CharField(
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )


class PictureQuizForm(forms.Form, QuizQuestionsValidator):
    quiz_model = PictureQuizEntity
    title = forms.CharField(
        required=True,
        max_length=255,
        min_length=10,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )


class PictureQuestionForm(forms.Form):
    # This serves as a widget
    # Checking for value is done in clean
    pics = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'q-ctrl'}),
    )
    # Proper container for uploaded files
    pic1 = forms.ImageField(required=False)
    pic2 = forms.ImageField(required=False)
    pic3 = forms.ImageField(required=False)
    pic4 = forms.ImageField(required=False)
    ref = forms.CharField(required=False)
    answer = forms.CharField(
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )
    clue = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )

    def clean(self):
        super().clean()
        ref_is_blank = str(self.cleaned_data.get('ref')).strip() == ''
        if ref_is_blank and self.cleaned_data.get('pics') is None:
            self.add_error('pics', ValidationError('There must be 4 pictures.'))
        elif ref_is_blank or self.cleaned_data.get('pics') is not None:
            for ctr in range(4):
                field_name = 'pic{}'.format(ctr + 1)
                pic = self.cleaned_data.get(field_name)
                if pic is None:
                    self.add_error('pics', ValidationError('There must be 4 pictures.'))
                elif pic.content_type not in ['image/jpeg', 'image/png']:
                    self.add_error('pics', ValidationError('File can only be jpeg or png.'))
                elif int(pic.size) > (10 * 1024 * 1024):
                    self.add_error('pics', ValidationError('File cannot be larger than 10Mb.'))
                if self.has_error('pics'):
                    return self.cleaned_data
        return self.cleaned_data


class VideoQuizForm(forms.Form, QuizQuestionsValidator):
    quiz_model = VideoQuizEntity
    title = forms.CharField(
        required=True,
        max_length=255,
        min_length=10,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )


class VideoQuestionForm(forms.Form):
    video = forms.CharField(
        required=True,
        max_length=32,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'}),
        validators=[RegexValidator(r'^[a-zA-Z0-9\-\_]+$', 'Not a valid Youtube video ID')]
    )
    question = forms.CharField(
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )
    answer = forms.CharField(
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )
    choices = forms.CharField(
        required=True,
        max_length=512,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )

    def clean(self):
        super().clean()
        dummy_choices_len = len(self.dummy_choices_as_list())
        if dummy_choices_len != 3:
            self.add_error('choices', ValidationError('Must exactly be 3, separated by commas.'))
        return self.cleaned_data

    def dummy_choices_as_list(self):
        return list(map(lambda x: str.strip(x), str(self.cleaned_data.get('choices')).split(',')))


class ResponseForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=48,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )
    email = forms.EmailField(
        required=True,
        max_length=72,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )


class ResponseItemForm(forms.Form):
    ref = forms.IntegerField(
        required=True,
    )
    answer = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'q-ctrl'})
    )

