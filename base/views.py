from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AdminRegistrationForm, StaffRegistrationForm, UploadCsvForm
from .models import Admin, Student
import csv

# Callables for user_passes_test()

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def is_staff(user):
    return user.groups.filter(name='STAFF').exists()



# Create your views here.


@user_passes_test(lambda u: u.is_superuser)
def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return render(request, 'register.html', {'register_form': form})
        messages.error(request, 'Registration unsuccessful.')
    else:
        form = AdminRegistrationForm()
    return render(request, 'admin-register.html', {'register_form': form})


def staff_register(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('base:login')
        messages.error(request, 'Registration unsuccessful.')
    else:
        form = StaffRegistrationForm()
    return render(request, 'staff-register.html', {'register_form': form})


def login_request(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'admin-register.html')
        if is_admin(request.user):
            return render(request, 'admin-home.html')
        if is_staff(request.user):
            return render(request, 'staff-home.html')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {username}.')
                if user.is_superuser:
                    return redirect('base:superuser-home')
                if is_admin(user):
                    return redirect('base:admin-home')
                if is_staff(user):
                    return redirect('base:staff-home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    form = AuthenticationForm()
    return render(request, 'login.html', {'login_form' : form})


def logout_request(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('base:login')


def staff_home(request):
    return render(request, 'staff-home.html')


def admin_home(request):
    form = UploadCsvForm()
    if request.method == 'POST':
        form = UploadCsvForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            current_user = request.user
            admin = Admin.objects.get(user=current_user)
            if not csv_file.name.endswith('.csv'):
                form.add_error('csv_file', 'File is not a CSV')
            else:
                try:
                    decoded_file = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(decoded_file)
                    for row in reader:
                        name = row['name']
                        student = Student.objects.create(name=name, school=admin.school)
                        student.save()
                    # Optionally, redirect to another page after upload
                    return redirect('base:admin-home')
                except Exception as e:
                    form.add_error('csv_file', 'Error processing file: ' + str(e))
    return render(request, 'admin-home.html', {'form': form})