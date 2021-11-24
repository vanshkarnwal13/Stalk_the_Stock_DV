from django.forms import ModelForm
from .models import UserDetail


class UserForm(ModelForm):
    class Meta:
        model = UserDetail
        fields = ['fname', 'lname', 'contact','purpose','city','plan']