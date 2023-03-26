from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AdminRegistrationForm, StaffRegistrationForm, UploadCsvForm, ReviewForm
from .models import Admin, Student, Staff, Review, Stats, Karma, Vote, Endorsement, EndorsementStats, Activity
import csv
import openai
import os
from dotenv import load_dotenv

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
    staff = Staff.objects.get(user=request.user)
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

    activities = Activity.objects.filter(staff=staff)
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
            karma = Karma.objects.get(student=student)
            karma.update_score()
            stats = Stats.objects.create(review=review) # every review object needs a stats object
            stats.save()
            # url_name = f"'base:student-profile' {student_name}"
            # action = '<a href="{% ' + 'url ' + url_name + ' %}">'
            activity = Activity.objects.create(
                staff=staff,
                message=f"You wrote a review for {student_name}.",
                action=""
                # action="{}".format(url)
            )
            activity.save()
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
                karma = Karma.objects.get(student=student)
            karma.update_score()
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
                karma = Karma.objects.get(student=review.student)
                karma.update_score()
                if vote_value == "UP":
                    activity = Activity.objects.create(
                        staff=review.staff,
                        message=f"Your review for {review.student.name} received an upvote."
                    )
                    activity.save()
                elif vote_value == "DOWN":
                    activity = Activity.objects.create(
                        staff=review.staff,
                        message=f"Your review for {review.student.name} received a downvote."
                    )
                    activity.save()
        except Vote.DoesNotExist:
            vote = Vote.objects.create(staff=staff, review=review, value=vote_value)
            vote.save()
            karma = Karma.objects.get(student=review.student)
            karma.update_score()
            if vote_value == "UP":
                activity = Activity.objects.create(
                    staff=review.staff,
                    message=f"Your review for {review.student.name} received an upvote."
                )
                activity.save()
            elif vote_value == "DOWN":
                activity = Activity.objects.create(
                    staff=review.staff,
                    message=f"Your review for {review.student.name} received a downvote."
                )
                activity.save()
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
                if endorsements.leadership:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You gave a leadership endorsement to {student_name}.",
                        action=""
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You removed a leadership endorsement from {student_name}.",
                        action=""
                    )
                    activity.save()
            elif skill == 'respect':
                endorsements.respect = not endorsements.respect
                if endorsements.respect:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You gave a respect endorsement to {student_name}.",
                        action=""
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You removed a respect endorsement from {student_name}.",
                        action=""
                    )
                    activity.save()
            elif skill == 'punctuality':
                endorsements.punctuality = not endorsements.punctuality
                if endorsements.punctuality:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You gave a punctuality endorsement to {student_name}.",
                        action=""
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You removed a punctuality endorsement from {student_name}.",
                        action=""
                    )
                    activity.save()
            elif skill == 'participation':
                endorsements.participation = not endorsements.participation
                if endorsements.participation:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You gave a participation endorsement to {student_name}.",
                        action=""
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You removed a participation endorsement from {student_name}.",
                        action=""
                    )
                    activity.save()
            elif skill == 'teamwork':
                endorsements.teamwork = not endorsements.teamwork
                if endorsements.teamwork:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You gave a teamwork endorsement to {student_name}.",
                        action=""
                    )
                    activity.save()
                else:
                    activity = Activity.objects.create(
                        staff=staff,
                        message=f"You removed a teamwork endorsement from {student_name}.",
                        action=""
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
                    staff=staff,
                    message=f"You gave a leadership endorsement to {student_name}.",
                    action=""
                )
                activity.save()
            elif skill == 'respect':
                endorsements.respect = True
                activity = Activity.objects.create(
                    staff=staff,
                    message=f"You gave a respect endorsement to {student_name}.",
                    action=""
                )
                activity.save()
            elif skill == 'punctuality':
                endorsements.punctuality = True
                activity = Activity.objects.create(
                    staff=staff,
                    message=f"You gave a punctuality endorsement to {student_name}.",
                    action=""
                )
                activity.save()
            elif skill == 'participation':
                endorsements.participation = True
                activity = Activity.objects.create(
                    staff=staff,
                    message=f"You gave a participation endorsement to {student_name}.",
                    action=""
                )
                activity.save()
            elif skill == 'teamwork':
                endorsements.teamwork = True
                activity = Activity.objects.create(
                    staff=staff,
                    message=f"You gave a teamwork endorsement to {student_name}.",
                    action=""
                )
                activity.save()
            endorsements.save()
            karma = Karma.objects.get(student=student)
            karma.update_score()
    return redirect('base:student-profile', student_name=student_name)


# Karma Leaderboard

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def student_ranking(request):
    staff = Staff.objects.get(user=request.user)
    students = Student.objects.filter(school=staff.school).order_by('-karma__score')
    context = {'students': students}
    return render(request, 'leaderboard.html', context)

# Generate Recommendation Letters

@login_required()
@user_passes_test(is_staff, login_url='/unauthorized')
def generate_recommendation(request, student_name):
    load_dotenv()
    openai.api_key= os.getenv('OPENAI_API_KEY')
    staff = Staff.objects.get(user=request.user)
    student = Student.objects.get(name=student_name, school=staff.school)
    karma=student.karma

    students = Student.objects.filter(school=staff.school).order_by('-karma__score')
    top_student=students[0] #get student with highest karma score
    max_karma=top_student.karma
    rank=karma.score/max_karma.score

    endorsement_stats= student.endorsementstats
    qualities=[]
    if endorsement_stats.leadership>0: 
        qualities.append("leadership")
    if endorsement_stats.respect>0:
        qualities.append("respect")
    if endorsement_stats.punctuality>0:
        qualities.append("punctuality")
    if endorsement_stats.participation>0:
        qualities.append("participation")
    if endorsement_stats.teamwork>0:
        qualities.append("teamwork")
    
    q=""
    if len(qualities)==0:
        q="[qualities/traits/skills]"
    else:
        length=len(qualities)
        for i in range (length-1):
            q+= qualities[i] +", "
        q+= "and " + qualities[length-1]

    if rank>=0.5:   # Excellent
        keywords="excellent, exemplary, outstanding, remarkable, model"
    elif rank>0:
        keywords="good, great, well"
    else:   #negative karma score
        keywords="fair"
    
    prompt= f"Write a recommendation letter for a student named {student_name} who attended {staff.school} using the words {keywords}"
    
    template=f"Dear [Recipient's Name],\n\nI am writing to recommend {student_name} for [Purpose of Recommendation] for which he/she has applied. I have had the pleasure of [teaching/supervising/working with] {student_name} for [length of time] at {staff.school}.\n\n During this time, I have had the opportunity to observe {student_name}'s exceptional {q}, which make him/her an outstanding candidate for [Purpose of Recommendation]. Specifically, [provide specific examples of the student's accomplishments or characteristics that demonstrate their suitability for the program or opportunity].\n\nIn addition to {student_name}'s exceptional {q}, he/she also possesses [other relevant qualities or characteristics, such as strong work ethic, leadership ability, creativity, or interpersonal skills]. These attributes have been critical to his/her success and have helped [him/her] to stand out as an exceptional student. Overall, I believe that {student_name} would be an excellent candidate for [Purpose of Recommendation], and I wholeheartedly endorse his/her application.\n\nIf you have any further questions or require additional information, please do not hesitate to contact me.\n\n Sincerely,\n{staff.user.get_full_name()}"

    if (request.method=='GET') & (rank>0):  #only use api if student has positive karma
        try:
            response= openai.Completion.create(
                model="text-davinci-003",
                prompt= prompt,
                max_tokens=1000,
                temperature=0
            )
            for result in response.choices:
                text=result.text    #to get and keep the last value in the {}

            context={
                'response':text,
                'message':"Sucessful"
            }
            return render (request,'recommendation-letter.html',context)
        except:
            context={
                'response':template,
                'message':"Exception block"
            }
            return render (request,'recommendation-letter.html',context)
    elif request.method=='GET' & rank<0: #for students with negative karma
        context={
                'response':template,
                'message':"Successful"
            }
        return render (request,'recommendation-letter.html',context)
    else:    #request is post
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
                            endorsement_stats = EndorsementStats.objects.create(student=student)  # create an endorsementstats object for each student
                            endorsement_stats.save()
                    return redirect('base:admin-home')
                except Exception as e:
                    form.add_error('csv_file', 'Error processing file: ' + str(e))
    return render(request, 'admin-home.html', {'form': form})

# ------------------ END OF SCHOOL ADMIN VIEWS ----------------------