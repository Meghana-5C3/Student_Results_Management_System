"""
URL configuration for StudentResultManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from resultapp.views import index,admin_login,admin_dashboard
from resultapp.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from resultapp.views import notice_detail



urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/',index,name='home'),
    path("notices/", notice_list, name="notice_list"),

    path('admin-login/',admin_login,name='admin-login'),
    path('admin_dashboard/',admin_dashboard,name='admin_dashboard'),
    path('create_class/',create_class,name='create_class'),
    path('admin_logout/',admin_logout,name='admin_logout'),
    path("",index, name="index"),  # root path
    path('manage_classes/',manage_classes,name='manage_classes'),
    path('edit_class/<int:class_id>/',edit_class,name='edit_class'),
    path('create_subject/',create_subject,name='create_subject'),
    path('manage_subjects/',manage_subjects,name='manage_subjects'),
    path('edit_subject/<int:subject_id>/',edit_subject,name='edit_subject'),
    path('add_subject_combination/',add_subject_combination,name='add_subject_combination'),
    path('manage_subject_combinations/',manage_subject_combinations,name='manage_subject_combinations'),
    path('edit-subject-combination/<int:combo_id>/', edit_subject_combination, name='edit_subject_combination'),
    path('add_student/',add_student,name='add_student'),
    path("manage_students/", manage_students, name="manage_students"),
    path('edit_student/<int:student_id>/', edit_student, name='edit_student'),
    path('add_result/', add_result, name='add_result'),
    path('manage_results/', manage_results, name='manage_results'),
    path('edit_result/<int:result_id>/', edit_result, name='edit_result'),
    path('delete_result/<int:result_id>/', delete_result, name='delete_result'),
    path('delete_subject/<int:subject_id>/', delete_subject, name='delete_subject'),
    path('delete-subject-combination/<int:id>/', delete_subject_combination, name='delete_subject_combination'),

    path('notices/edit/<int:notice_id>/', edit_notice, name='edit_notice'),

    path('notices/add/', add_notice, name='add_notice'),
    path('notices/manage/', manage_notices, name='manage_notices'),
    path('notices/<int:notice_id>/', notice_detail, name='notice_detail'),


path(
    'password/change/',
    auth_views.PasswordChangeView.as_view(
        template_name='auth/password_change_form.html'
    ),
    name='password_change'
),
path(
    'password/change/done/',
    auth_views.PasswordChangeDoneView.as_view(
        template_name='auth/password_change_done.html'
    ),
    name='password_change_done'
),
path('student_results/', student_results, name='student_results'),
 
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name="auth/password_reset.html"), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"), 
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"), 
         name='password_reset_confirm'),

    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"), 
         name='password_reset_complete'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)