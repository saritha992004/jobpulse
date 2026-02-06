from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import JobApplication


from datetime import date
from django.db.models import Q

def home(request):
    return render(request, 'tracker/home.html')

from django.contrib.auth.models import User
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        User.objects.create_user(
            username=username,
            password=password1
        )

        messages.success(request, "Account created successfully")
        return redirect('login')

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




from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date

@login_required
def dashboard(request):
    query = request.GET.get('q', '')          # search text
    status = request.GET.get('status', '')    # status filter

    jobs = JobApplication.objects.filter(user=request.user)

    # 🔍 Search filter
    if query:
        jobs = jobs.filter(
            Q(company__icontains=query) |
            Q(role__icontains=query) |
            Q(status__icontains=query)
        )

    # 🎯 Status filter
    if status:
        jobs = jobs.filter(status=status)

    # 📊 Stats
    total = jobs.count()
    interviews = jobs.filter(status='Interview').count()
    rejected = jobs.filter(status='Rejected').count()

    context = {
        'jobs': jobs,
        'total': total,
        'interviews': interviews,
        'rejected': rejected,
        'today': date.today(),
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
            followup_date=request.POST.get('followup_date') or None,
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
        job.followup_date = request.POST.get('followup_date') or None
        job.notes = request.POST.get('notes', '')
        job.save()
        return redirect('dashboard')

    return render(request, 'tracker/edit_job.html', {'job': job})


@login_required
def delete_job(request, job_id):
    job = JobApplication.objects.get(id=job_id, user=request.user)
    job.delete()
    return redirect('dashboard')

import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def add_from_email(request):
    if request.method == "POST":
        email_text = request.POST.get("email_text", "")

        role = "Unknown Role"
        company = "Unknown Company"

        # Role patterns
        role_patterns = [
            r'position of ([A-Za-z\s]+)',
            r'for the role of ([A-Za-z\s]+)',
            r'for ([A-Za-z\s]+) at',
            r'applied for ([A-Za-z\s]+)',
        ]

        for pattern in role_patterns:
            match = re.search(pattern, email_text, re.IGNORECASE)
            if match:
                role = match.group(1).strip()
                break

        # Company patterns
        company_patterns = [
            r'at ([A-Za-z0-9\s]+)',
            r'with ([A-Za-z0-9\s]+)',
            r'to ([A-Za-z0-9\s]+)',
        ]

        for pattern in company_patterns:
            match = re.search(pattern, email_text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                break

        JobApplication.objects.create(
            user=request.user,
            company=company,
            role=role,
            status="Applied"
        )

        return redirect("dashboard")

    return render(request, "tracker/add_from_email.html")
