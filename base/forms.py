from django import forms
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, Row, Column, Div
from .models import Admin, Staff, School, Student, Review


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

        return admin

    #checks if email already exists in the database
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email


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

        return staff

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
        self.helper.form_action = reverse('base:student-upload')

        self.helper.layout = Layout(
            Field('csv_file'),
            Div(
                Submit('submit', 'Upload'), css_class="d-flex justify-content-end"
            )
        )


class StudentForm(forms.ModelForm):
    school = forms.ModelChoiceField(
        widget=forms.HiddenInput(),
        queryset=School.objects.all(),
        required=True
    )

    class Meta:
        model = Student
        fields = ('name', 'school')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].disabled = True

    # def save(self, commit=True):
    #     student = super(StudentForm, self).save(commit=False)
    #     student.name = self.cleaned_data['name']
    #     if commit:
    #         student.save()
    #     return student

    # def clean_name(self):
    #     name = self.cleaned_data.get('name')
    #     school = self.cleaned_data.get('school')
    #     if Student.objects.filter(name=name, school=school).exists():
    #         raise forms.ValidationError("Student has already been added.")
    #     return name

    # def clean(self):
    #     cleaned_data = super().clean()
    #     name = self.cleaned_data['name']
    #     school = self.cleaned_data['school']
    #     if Student.objects.filter(name=name, school=school).exists():
    #         raise forms.ValidationError("Student has already been added.")
    #     return name

    # def is_valid(self):
    #     name = self.cleaned_data.get('name')
    #     school = self.cleaned_data.get('school')
    #     if Student.objects.filter(name=name, school=school).exists():
    #         raise forms.ValidationError("Student has already been added.")
    #     return super(OrderTestForm, self).is_valid()



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
        self.fields['text'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter review text (50 characters minimum)'})
        self.fields['rating'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter rating out of 5'})
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating



#form for recommendation letter
class LetterForm(forms.Form):
    response = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'letter-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False
        self.helper.add_input(Submit('submit', 'Download'))

        self.helper.layout = Layout(
            Field('response', rows='25')
        )
