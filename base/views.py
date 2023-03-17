from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AdminRegistrationForm, StaffRegistrationForm, UploadCsvForm
from .models import Admin, Student, Staff
import csv

# Callables for user_passes_test()

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def is_staff(user):
    return user.groups.filter(name='STAFF').exists()



# Create your views here.


def login_request(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('base:superuser-home')
        if is_admin(request.user):
            return redirect('base:admin-home')
        if is_staff(request.user):
            return redirect('base:staff-home')
    else:
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
                        messages.info(request, 'Superuser logged in')
                        return redirect('base:superuser-home')
                    if is_admin(user):
                        messages.info(request, 'Admin logged in')
                        return redirect('base:admin-home')
                    if is_staff(user):
                        messages.info(request, 'Staff logged in')
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


# View for when a user attempts to access a view that they are not authorized to

def unauthorized(request):
    return render(request, 'unauthorized.html')


# def index(request):
#     if request.user.is_authenticated:
#         if request.user.is_superuser:
#             return redirect('base:superuser-home')
#         if is_admin(request.user):
#             return redirect('base:admin-home')
#         if is_staff(request.user):
#             return redirect('base:staff-home')
#     else:
#         return redirect('base:login')



# ------------------ SUPERUSER VIEWS ----------------------

# Admin registration view - allows authenticated superusers to create school admin accounts

@login_required()
@user_passes_test(lambda u: u.is_superuser, login_url='/unauthorized')
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

# ------------------ END OF SUPERUSER VIEWS ----------------------



# ------------------ SCHOOL STAFF VIEWS ----------------------

# Staff registration view - allows school staff (eg. teachers) to create accounts

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


@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def staff_home(request):
    return render(request, 'staff-home.html')


# Search for students - allows school staff to search for students in their school

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def student_search(request):
    query = request.GET.get('query')
    current_user = request.user
    staff = Staff.objects.get(user=current_user)
    # search for items matching the query
    search_results = Student.objects.filter(name__icontains=query, school=staff.school)
    context = {'query' : query, 'search_results' : search_results}
    return render(request, 'search-results.html', context)


def student_profile(request, student_name):
    student = Student.objects.get(name=student_name)
    return render(request, 'student-profile.html', context={'student':student})

# ------------------ END OF SCHOOL STAFF VIEWS ----------------------



# ------------------ SCHOOL ADMIN VIEWS ----------------------

# School admin homepage / csv upload form - allows school admins to upload a csv file
# with student names to populate the Student table

@login_required()
@user_passes_test(is_admin, login_url='/unauthorized')
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
                    decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
                    reader = csv.DictReader(decoded_file)
                    for row in reader:
                        messages.info(request, f"{row}")
                        name = row['name']
                        if not Student.objects.filter(name=name, school=admin.school).exists():
                            student = Student.objects.create(name=name, school=admin.school)
                            student.save()
                    return redirect('base:admin-home')
                except Exception as e:
                    form.add_error('csv_file', 'Error processing file: ' + str(e))
    return render(request, 'admin-home.html', {'form': form})

# ------------------ END OF SCHOOL ADMIN VIEWS ----------------------