from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AdminRegistrationForm, StaffRegistrationForm, UploadCsvForm, ReviewForm
from .models import Admin, Student, Staff, Review, Stats, Karma, Vote, Endorsement, EndorsementStats
import csv
import os
import openai
from django.conf import settings

openai.api_key = settings.OPEN_API_KEY

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
    context = {
        'query' : query,
        'search_results' : search_results
    }
    return render(request, 'search-results.html', context)


# Show student profile

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def student_profile(request, student_name):
    staff = Staff.objects.get(user=request.user)
    student = Student.objects.get(name=student_name, school=staff.school)
    karma = student.karma
    reviews = Review.objects.filter(student=student)
    endorsement_stats = student.endorsementstats

    highest_endorsements = {
        'leadership' : 0,
        'respect' : 0,
        'punctuality' : 0,
        'participation' : 0,
        'teamwork' : 0
    }
    all_endorsement_stats = [stats for stats in EndorsementStats.objects.all() if stats.school==staff.school]
    for stats in all_endorsement_stats:
        if stats.leadership > highest_endorsements['leadership']:
            highest_endorsements['leadership'] = stats.leadership
        if stats.respect > highest_endorsements['respect']:
            highest_endorsements['respect'] = stats.respect
        if stats.punctuality > highest_endorsements['punctuality']:
            highest_endorsements['punctuality'] = stats.punctuality
        if stats.participation > highest_endorsements['participation']:
            highest_endorsements['participation'] = stats.participation
        if stats.teamwork > highest_endorsements['teamwork']:
            highest_endorsements['teamwork'] = stats.teamwork

    context = {
        'student' : student,
        'karma' : karma,
        'endorsement_stats' : endorsement_stats,
        'highest_endorsements' : highest_endorsements,
        'reviews' : reviews
    }
    return render(request, 'student-profile.html', context)



# Write a review for a student

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def create_review(request, student_name):
    staff = Staff.objects.get(user=request.user)
    student = Student.objects.get(name=student_name, school=staff.school)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.staff = staff
            review.student = student
            review.is_good = review.rating >= 3
            review.save()
            stats = Stats.objects.create(review=review) # every review object needs a stats object
            stats.save()
            messages.success(request, 'Your review has been added!')
            return redirect('base:student-profile', student_name=student_name)
    else:
        form = ReviewForm()
    context = {
        'form' : form,
        'student' : student
    }
    return render(request, 'create-review.html', context)


# Edit Review: allow a staff member to change a review that they already posted

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def edit_review(request, review_pk):
    review= Review.objects.get(pk=review_pk)
    data={
        'text': review.text,
        'rating': review.rating
    }
    form=ReviewForm(data, initial=data)
    if request.method=='GET':
        return render(request, 'edit-review.html', data)
    else:   #if it was a POST request
        if form.has_changed():  #checks if the data is different
            if form.is_valid():
                review = form.save(commit=False)
                review.is_good = review.rating >= 3
                review.edited=True
                review.save()   #hit the database
        return redirect('base:staff-home')


# Vote on a review

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def vote_review(request, review_id, vote_value):
    if request.method == "POST":
        review = Review.objects.get(id=review_id)
        staff = Staff.objects.get(user=request.user)
        try:
            vote = Vote.objects.get(staff=staff, review=review)
            if vote.value != vote_value:
                vote.delete()
                vote = Vote.objects.create(staff=staff, review=review, value=vote_value)
                vote.save()
        except Vote.DoesNotExist:
            vote = Vote.objects.create(staff=staff, review=review, value=vote_value)
            vote.save()
    return redirect('base:student-profile', student_name=review.student.name)


# Give a student a skill endorsement

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def give_endorsement(request, student_name, skill):
    if request.method == "POST":
        staff = Staff.objects.get(user=request.user)
        student = Student.objects.get(name=student_name, school=staff.school)
        try:
            endorsements = Endorsement.objects.get(student=student, staff=staff)
            if skill == 'leadership':
                endorsements.leadership = not endorsements.leadership
            elif skill == 'respect':
                endorsements.respect = not endorsements.respect
            elif skill == 'punctuality':
                endorsements.punctuality = not endorsements.punctuality
            elif skill == 'participation':
                endorsements.participation = not endorsements.participation
            elif skill == 'teamwork':
                endorsements.teamwork = not endorsements.teamwork
            endorsements.save()
        except Endorsement.DoesNotExist:
            endorsements = Endorsement.objects.create(student=student, staff=staff)
            if skill == 'leadership':
                endorsements.leadership = not endorsements.leadership
            elif skill == 'respect':
                endorsements.respect = not endorsements.respect
            elif skill == 'punctuality':
                endorsements.punctuality = not endorsements.punctuality
            elif skill == 'participation':
                endorsements.participation = not endorsements.participation
            elif skill == 'teamwork':
                endorsements.teamwork = not endorsements.teamwork
            endorsements.save()
    return redirect('base:student-profile', student_name=student_name)

#   generate recommendation letters
@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def generate_recommendation(request, student_name):
    staff = Staff.objects.get(user=request.user)
    student = Student.objects.get(name=student_name, school=staff.school)
    karma=student.karma

    students = Student.objects.filter(school=staff.school).order_by('-karma__score')
    top_student=students[0] #get student with highest karma score
    max_karma=top_student.karma
    rank=karma/max_karma

    if rank>=0.5:
        type=1  # Excellent
    elif rank>0:
        type=2  # Good
    else:   #negative karma score
        type=3  # Poor

    if request.method=='GET':
        try:
            response= openai.Completion.create(
                model="text-davinci-003",
                prompt="Say this is a test",
                max_tokens=100,
                temperature=0
            )
            for result in response.choices:
                text=result.text    #to get and keep the last value in the {}

            context={
                'response':text,
                'rank':rank,
                'type':type,
                'message':"Sucessful post"
            }
            return render (request,'recommendation-letter.html',context)
        except:
            context={
                'response':"Server Unavailable",
                'message':"Exception block"
            }
            return render (request,'recommendation-letter.html',context)
    else:
        context={
                'response':"This is a post request",
                'message':"post request"
            }
        return render (request,'recommendation-letter.html',context)
    

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
                            karma = Karma.objects.create(student=student) # create a karma object for each student
                            karma.save()
                            endstats= EndorsementStats.objects.create(student=student)  # create an endstats object for each student
                            endstats.save()
                    return redirect('base:admin-home')
                except Exception as e:
                    form.add_error('csv_file', 'Error processing file: ' + str(e))
    return render(request, 'admin-home.html', {'form': form})

# ------------------ END OF SCHOOL ADMIN VIEWS ----------------------