from django import forms

from .models import Choice, Poll


class PollForm(forms.ModelForm):
    choice1 = forms.CharField(
        label='Вариант 1',
        max_length=100,
        min_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    choice2 = forms.CharField(
        label='Вариант 2',
        max_length=100,
        min_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    choice3 = forms.CharField(
        label='Вариант 3',
        max_length=100,
        min_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    choice4 = forms.CharField(
        label='Вариант 4',
        max_length=100,
        min_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Poll
        fields = ['text', 'choice1', 'choice2', 'choice3', 'choice4']
        widgets = {
            'text': forms.Textarea(attrs={"class": "form-control", "rows": 5, "cols": 20})
        }


class EditPollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={"class": "form-control", "rows": 5, "cols": 20})
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']
