from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AdminRegistrationForm, StaffRegistrationForm

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

# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         staff_reg_form = StaffRegisterForm(request.POST)
#         if form.is_valid() and staff_reg_form.is_valid():
#             user = form.save()
#             user.refresh_from_db()
#             staff_reg_form = StaffRegisterForm(request.POST, instance=user.staff)
#             staff_reg_form.full_clean()
#             staff_reg_form.save()
#             messages.success(request, f'Your account has been successfully created!')
#             return redirect('login')
#     else:
#         form = UserRegisterForm()
#         staff_reg_form = StaffRegisterForm()
#         context = {
#             'form' : form,
#             'staff_reg_form' : staff_reg_form
#         }
#     return render(request, 'base/templates/register.html', context)

def login_request(request):
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

def staff_home(request):
    return render(request, 'staff-home.html')

def admin_home(request):
    return render(request, 'admin-home.html')