from django.urls import path
from .views import home, register_view, login_view, logout_view, dashboard, add_job, edit_job, delete_job, \
    add_from_email

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('add-job/', add_job, name='add_job'),
    path('edit/<int:job_id>/', edit_job, name='edit_job'),
    path('delete/<int:job_id>/', delete_job, name='delete_job'),
    path('add-from-email/',add_from_email, name='add_from_email'),


]
