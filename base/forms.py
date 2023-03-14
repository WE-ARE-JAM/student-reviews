from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Admin, Staff, School

class AdminRegistrationForm(UserCreationForm):
    school = forms.ModelChoiceField(queryset=School.objects.all(), required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=32, required=True)
    last_name = forms.CharField(max_length=32, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(AdminRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        admin = Admin.objects.create(user=user, school=self.cleaned_data['school'])
        admin.save()

        # adding user to ADMIN group
        admin_group, created = Group.objects.get_or_create(name="ADMIN")
        user.groups.add(admin_group)

        return user


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


class UploadCsvForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV file')