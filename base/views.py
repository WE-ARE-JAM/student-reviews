from django.shortcuts import render
from .forms import UserRegisterForm, StaffRegisterForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        staff_reg_form = StaffRegisterForm(request.POST)
        if form.is_valid() and staff_reg_form.is_valid():
            user = form.save()
            user.refresh_from_db()
            staff_reg_form = StaffRegisterForm(request.POST, instance=user.staff)
            staff_reg_form.full_clean()
            staff_reg_form.save()
            messages.success(request, f'Your account has been successfully created!')
            return redirect('login')
    else:
        form = UserRegisterForm()
        staff_reg_form = StaffRegisterForm()
        context = {
            'form' : form,
            'staff_reg_form' : staff_reg_form
        }
    return render(request, 'base/templates/register.html', context)
