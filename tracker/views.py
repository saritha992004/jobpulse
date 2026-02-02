from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import JobApplication
from django.shortcuts import render

from datetime import date
from django.db.models import Q

def home(request):
    return render(request, 'tracker/home.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            User.objects.create_user(username=username, password=password1)
            messages.success(request, "Account created successfully")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match")

    return render(request, 'tracker/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'tracker/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')




@login_required
def dashboard(request):
    query = request.GET.get('q', '')       # Search query
    status = request.GET.get('status')     # Status filter

    jobs = JobApplication.objects.filter(user=request.user)

    # Apply search filter
    if query:
        jobs = jobs.filter(
            Q(company__icontains=query) |
            Q(role__icontains=query)
        )

    # Apply status filter
    if status:
        jobs = jobs.filter(status=status)   # <-- ITHU INGA paste pannunga

    # Stats for chart/cards
    total = jobs.count()
    interviews = jobs.filter(status='Interview').count()
    rejected = jobs.filter(status='Rejected').count()

    today = date.today()

    context = {
        'jobs': jobs,
        'total': total,
        'interviews': interviews,
        'rejected': rejected,
        'today': today,
        'query': query,
        'status': status,
    }

    return render(request, 'tracker/dashboard.html', context)



@login_required
def add_job(request):
    if request.method == 'POST':
        JobApplication.objects.create(
            user=request.user,
            company=request.POST['company'],
            role=request.POST['role'],
            status=request.POST['status'],
            followup_date=request.POST.get('followup') or None,
            notes=request.POST.get('notes', '')
        )

        return redirect('dashboard')

    return render(request, 'tracker/add_job.html')


@login_required
def edit_job(request, job_id):
    job = JobApplication.objects.get(id=job_id, user=request.user)

    if request.method == 'POST':
        job.company = request.POST['company']
        job.role = request.POST['role']
        job.status = request.POST['status']
        job.followup_date = request.POST.get('followup') or None
        job.notes = request.POST.get('notes', '')
        job.save()
        return redirect('dashboard')

    return render(request, 'tracker/edit_job.html', {'job': job})


@login_required
def delete_job(request, job_id):
    job = JobApplication.objects.get(id=job_id, user=request.user)
    job.delete()
    return redirect('dashboard')

