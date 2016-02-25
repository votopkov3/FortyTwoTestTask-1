from django import forms
from models import Profile
from widgets import DatePickerWidget


class ProfileForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(max_length=100,
                           min_length=3,
                           widget=forms.TextInput(
                               attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100,
                                min_length=3,
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(widget=DatePickerWidget(
        params="dateFormat: 'yy-mm-dd', changeYear: true,"
               " defaultDate: 'c-25', yearRange: 'c-115:c'",
        attrs={'class': 'datepicker'}))
    photo = forms.ImageField(required=False,
                             widget=forms.FileInput)
    email = forms.EmailField(max_length=100,
                             widget=forms.TextInput(attrs={'class':
                                                           'form-control'}))
    jabber = forms.EmailField(max_length=100,
                              min_length=3,
                              widget=forms.TextInput(attrs={'class':
                                                            'form-control'}))
    skype = forms.CharField(max_length=100,
                            min_length=3,
                            widget=forms.TextInput(attrs={'class':
                                                          'form-control'}))
    other_contacts = forms.CharField(max_length=1000,
                                     required=False,
                                     widget=forms.Textarea(
                                         attrs={'class':
                                                'form-control'}))
    bio = forms.CharField(max_length=1000,
                          required=False,
                          widget=forms.Textarea(
                              attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['id', 'name', 'last_name',
                  'date_of_birth', 'photo', 'bio',
                  'email', 'jabber', 'skype',
                  'other_contacts']
