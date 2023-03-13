from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Staff, School

class StaffRegistrationForm(UserCreationForm):
    school = forms.ModelChoiceField(queryset=School.objects.all(), required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=32, required=True)
    last_name = forms.CharField(max_length=32, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(StaffRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        staff = Staff.objects.create(user=user, school=self.cleaned_data['school'])
        staff.save()

        # adding user to STAFF group
        staff_group, created = Group.objects.get_or_create(name="STAFF")
        user.groups.add(staff_group)
        
        return user

# class UserRegisterForm(UserCreationForm):
#     email = forms.EmailField(required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']


# class StaffRegisterForm(forms.ModelForm):
#     class Meta:
#         model = Staff
#         fields = ['school']