# Rate My Students

![built-by-jam- _](https://user-images.githubusercontent.com/77900309/230798499-4ef99d38-5334-46eb-951e-6a70ad52146c.svg) ![built-with-django](https://user-images.githubusercontent.com/77900309/230798543-05f5f479-43d7-4450-84f4-2a46967ff46b.svg)

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/WE-ARE-JAM/student-reviews)

Rate My Students is a reviews site made for secondary school teachers in Trinidad & Tobago to review and assign ratings to their experiences with specific students.

## Background

Secondary school teachers often have to write recommendation letters for students, or nominate students for leadership positions, or select students to represent the school, and more. Rate My Students aims to assist teachers in these activities by providing a website where teachers can review and rate experiences with their students, give skill endorsements to students, and vote on reviews. These actions can increase or decrease a student's karma score, a metric of how "good" or "bad" a student is.

## Key Features

- Supports 3 types of users: the superuser (JAM), school admins, and school teachers (staff)
- Records and displays superuser activity and staff activity
- Allows the superuser to register schools and school admins
- School admins can upload students via a CSV file or add students by manually entering student names
- School staff can:
  - Search for students
  - Give/Rescind skill endorsements to/from students
  - Write/Edit/Delete reviews for students
  - Upvote/Downvote reviews
  - Sort reviews
  - View a system-generated student summary for each student
  - View a Student Leaderboard
  - Download the Student Leaderboard as a PDF file
  - Query the Student Leaderboard for the Top x students
  - Generate and/or edit recommendation letters for students
  - Download recommendation letters as PDF files
  - Copy recommendation letters to clipboard

## Tech Stack

- [Django](https://www.djangoproject.com) framework for backend implementation
- [Bootstrap 5](https://getbootstrap.com) for frontend implementation
- PostgreSQL database
- [Railway](https://railway.app) for deployment
- [django-crispy-forms](https://django-crispy-forms.readthedocs.io/en/latest/) for rendering Django forms
- [django-safedelete](https://django-safedelete.readthedocs.io/en/latest/index.html) for logical (soft) deletion
- [django-mathfilters](https://pypi.org/project/django-mathfilters/) for performing simple arithmetic operations in Django templates
- [Open AI API](https://platform.openai.com/docs/introduction) for generating student summaries and recommendation letters

## Contributors

Rate My Students was built by JAM. Our team consists of [@joshuapj](https://github.com/joshuapj), [@LYS312](https://github.com/LYS312), and [@michelllle-liu](https://github.com/michelllle-liu)

### Michelle Liu 
GitHub [@michelllle-liu](https://github.com/michelllle-liu) &nbsp;&middot;&nbsp; [LinkedIn](https://www.linkedin.com/in/michelllle-liu/)
- Development Lead, Backend implementation, Frontend implementation, DevOps

### Alyssa Bharath
GitHub [@LYS312](https://github.com/LYS312) &nbsp;&middot;&nbsp; [LinkedIn](https://www.linkedin.com/in/alyssa-bharath-b9a7a1256/)
- Backend implementation

### Joshua Persad-John
GitHub [@joshuapj](https://github.com/joshuapj) &nbsp;&middot;&nbsp; [LinkedIn](https://www.linkedin.com/in/joshua-persad-john/)
- Testing
