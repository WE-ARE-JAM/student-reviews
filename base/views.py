from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import SchoolRegistrationForm, AdminRegistrationForm, StaffRegistrationForm, UploadCsvForm, ReviewForm
from .models import Admin, Student, Staff, Review, Stats, Karma, Vote, Endorsement, EndorsementStats, Activity
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

@login_required()
@user_passes_test(lambda u: u.is_superuser, login_url='/unauthorized')
def superuser_home(request):
    return render(request, 'superuser-home.html')



@login_required()
@user_passes_test(lambda u: u.is_superuser, login_url='/unauthorized')
def school_register(request):
    if request.method == 'POST':
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            school = form.save(commit=False)
            school.save()
            messages.success(request, 'School registration successful!')
            return redirect('base:superuser-home')
        messages.error(request, 'Oops, something went wrong :(')
    else:
        form = SchoolRegistrationForm()
    return render(request, 'school-register.html', {'form' : form})



# Admin registration view - allows authenticated superusers to create school admin accounts

@login_required()
@user_passes_test(lambda u: u.is_superuser, login_url='/unauthorized')
def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Admin registration successful!')
            return redirect('base:superuser-home')
        messages.error(request, 'Oops, something went wrong :(')
    else:
        form = AdminRegistrationForm()
    return render(request, 'admin-register.html', {'register_form' : form})

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
        messages.error(request, 'Oops, something went wrong :(')
    else:
        form = StaffRegistrationForm()
    return render(request, 'staff-register.html', {'register_form': form})


@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def staff_home(request):
    user = request.user
    staff = Staff.objects.get(user=user)
    reviews = Review.objects.filter(staff=staff)
    num_reviews = reviews.count()
    num_upvotes = 0
    num_downvotes = 0
    for review in reviews:
        num_upvotes += review.stats.upvotes
        num_downvotes += review.stats.downvotes
    
    endorsements = Endorsement.objects.filter(staff=staff)
    num_endorsements_given = 0
    for endorsement in endorsements:
        if endorsement.leadership: num_endorsements_given += 1
        if endorsement.respect: num_endorsements_given += 1
        if endorsement.punctuality: num_endorsements_given += 1
        if endorsement.participation: num_endorsements_given += 1
        if endorsement.teamwork: num_endorsements_given += 1

    activities = Activity.objects.filter(user=user)
    activities = sorted(list(activities), key=lambda x: x.created_at, reverse=True)

    context = {
        'num_reviews' : num_reviews,
        'num_upvotes' : num_upvotes,
        'num_downvotes' : num_downvotes,
        'num_endorsements' : num_endorsements_given,
        'activities' : activities
    }
    
    return render(request, 'staff-home.html', context)


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
    user = request.user
    staff = Staff.objects.get(user=user)
    student = Student.objects.get(name=student_name, school=staff.school)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.staff = staff
            review.student = student
            review.is_good = review.rating >= 3
            review.save()
            karma = Karma.objects.get(student=student)
            karma.update_score()
            stats = Stats.objects.create(review=review) # every review object needs a stats object
            stats.save()
            # url_name = f"'base:student-profile' {student_name}"
            # action = '<a href="{% ' + 'url ' + url_name + ' %}">'
            activity = Activity.objects.create(
                user=user,
                message=f"You wrote a review for {student_name}.",
                parameter=f"{student_name}"
                # action="{}".format(url)
            )
            activity.save()
            messages.success(request, 'Thank you for your review!')
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
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    user = request.user
    staff = Staff.objects.get(user=user)
    if staff != review.staff:
        return redirect('base:unauthorized')
    if request.method == 'POST':
        form = ReviewForm(instance=review, data=request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_good = review.rating >= 3
            review.edited = True
            review.save()
            karma = Karma.objects.get(student=review.student)
            karma.update_score()
            activity = Activity.objects.create(
                user=user,
                message=f"You edited your review for {review.student.name}.",
                parameter=f"{review.student.name}"
            )
            activity.save()
            return redirect('base:student-profile', student_name=review.student.name)
    else:
        form = ReviewForm(instance=review)
    context = {
        'form' : form,
        'student' : review.student
    }
    return render(request, 'edit-review.html', context)


# Vote on a review

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def vote_review(request, review_id, vote_value):
    if request.method == "POST":
        review = Review.objects.get(id=review_id)
        user = request.user
        staff = Staff.objects.get(user=user)
        try:
            vote = Vote.objects.get(staff=staff, review=review)
            if vote.value != vote_value:
                vote.delete()
                vote = Vote.objects.create(staff=staff, review=review, value=vote_value)
                vote.save()
                karma = Karma.objects.get(student=review.student)
                karma.update_score()
                if vote_value == "UP":
                    activity = Activity.objects.create(
                        user=user,
                        message=f"Your review for {review.student.name} received an upvote.",
                        parameter=f"{review.student.name}"
                    )
                    activity.save()
                elif vote_value == "DOWN":
                    activity = Activity.objects.create(
                        user=user,
                        message=f"Your review for {review.student.name} received a downvote.",
                        parameter=f"{review.student.name}"
                    )
                    activity.save()
        except Vote.DoesNotExist:
            vote = Vote.objects.create(staff=staff, review=review, value=vote_value)
            vote.save()
            karma = Karma.objects.get(student=review.student)
            karma.update_score()
            if vote_value == "UP":
                activity = Activity.objects.create(
                    user=user,
                    message=f"Your review for {review.student.name} received an upvote.",
                    parameter=f"{review.student.name}"
                )
                activity.save()
            elif vote_value == "DOWN":
                activity = Activity.objects.create(
                    user=user,
                    message=f"Your review for {review.student.name} received a downvote.",
                    parameter=f"{review.student.name}"
                )
                activity.save()
    return redirect('base:student-profile', student_name=review.student.name)


# Give a student a skill endorsement

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def give_endorsement(request, student_name, skill):
    if request.method == "POST":
        user = request.user
        staff = Staff.objects.get(user=user)
        student = Student.objects.get(name=student_name, school=staff.school)
        try:
            endorsements = Endorsement.objects.get(student=student, staff=staff)
            if skill == 'leadership':
                endorsements.leadership = not endorsements.leadership
                if endorsements.leadership:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You gave a leadership endorsement to {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You removed a leadership endorsement from {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
            elif skill == 'respect':
                endorsements.respect = not endorsements.respect
                if endorsements.respect:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You gave a respect endorsement to {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You removed a respect endorsement from {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
            elif skill == 'punctuality':
                endorsements.punctuality = not endorsements.punctuality
                if endorsements.punctuality:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You gave a punctuality endorsement to {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You removed a punctuality endorsement from {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
            elif skill == 'participation':
                endorsements.participation = not endorsements.participation
                if endorsements.participation:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You gave a participation endorsement to {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You removed a participation endorsement from {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
            elif skill == 'teamwork':
                endorsements.teamwork = not endorsements.teamwork
                if endorsements.teamwork:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You gave a teamwork endorsement to {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        user=user,
                        message=f"You removed a teamwork endorsement from {student_name}.",
                        parameter=f"{student.name}"
                    )
                    activity.save()
            endorsements.save()
            karma = Karma.objects.get(student=student)
            karma.update_score()
        except Endorsement.DoesNotExist:
            endorsements = Endorsement.objects.create(student=student, staff=staff)
            if skill == 'leadership':
                endorsements.leadership = True
                activity = Activity.objects.create(
                    user=user,
                    message=f"You gave a leadership endorsement to {student_name}.",
                    parameter=f"{student.name}"
                )
                activity.save()
            elif skill == 'respect':
                endorsements.respect = True
                activity = Activity.objects.create(
                    user=user,
                    message=f"You gave a respect endorsement to {student_name}.",
                    parameter=f"{student.name}"
                )
                activity.save()
            elif skill == 'punctuality':
                endorsements.punctuality = True
                activity = Activity.objects.create(
                    user=user,
                    message=f"You gave a punctuality endorsement to {student_name}.",
                    parameter=f"{student.name}"
                )
                activity.save()
            elif skill == 'participation':
                endorsements.participation = True
                activity = Activity.objects.create(
                    user=user,
                    message=f"You gave a participation endorsement to {student_name}.",
                    parameter=f"{student.name}"
                )
                activity.save()
            elif skill == 'teamwork':
                endorsements.teamwork = True
                activity = Activity.objects.create(
                    user=user,
                    message=f"You gave a teamwork endorsement to {student_name}.",
                    parameter=f"{student.name}"
                )
                activity.save()
            endorsements.save()
            karma = Karma.objects.get(student=student)
            karma.update_score()
    return redirect('base:student-profile', student_name=student_name)


@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def student_ranking(request):
    staff = Staff.objects.get(user=request.user)
    students = Student.objects.filter(school=staff.school).order_by('-karma__score')
    context = {'students': students}
    return render(request, 'leaderboard.html', context)

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
                        name = row['name']
                        if not Student.objects.filter(name=name, school=admin.school).exists():
                            student = Student.objects.create(name=name, school=admin.school)
                            student.save()
                            karma = Karma.objects.create(student=student) # create a karma object for each student
                            karma.save()
                            endorsement_stats = EndorsementStats.objects.create(student=student)  # create an endorsementstats object for each student
                            endorsement_stats.save()
                    return redirect('base:admin-home')
                except Exception as e:
                    form.add_error('csv_file', 'Error processing file: ' + str(e))
    return render(request, 'admin-home.html', {'form': form})

# ------------------ END OF SCHOOL ADMIN VIEWS ----------------------