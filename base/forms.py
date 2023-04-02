from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Admin, Staff, School, Review


class SchoolRegistrationForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ('name',)


# form for registering school admins (to be used by superusers only)
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


# form for registering school staff
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

    #checks if email already exists in the database
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email


# form for uploading .csv file with student names
class UploadCsvForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV file ')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'upload-csv'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'

        self.helper.add_input(Submit('submit', 'Upload'))


# form for writing a review for a student
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('text', 'rating')
        widgets = {
            'rating' : forms.NumberInput(attrs={'min':'1', 'max':'5'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter review text'})
        self.fields['rating'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter rating out of 5'})
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating
    