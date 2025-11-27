from django.urls import path
from . import views
from gamification import views

urlpatterns = [
    path("", views.home, name="home"),    # homepage
    path("dashboard/student/<slug:slug>/", views.student_dashboard, name="student_dashboard"), # Student dashboard
    path("dashboard/teacher/<slug:slug>/", views.teacher_dashboard, name="teacher_dashboard"), # Teacher dashboard
    path("category/<int:category_id>/subtopics/", views.explore_subtopics, name="explore_subtopics"), # Explore subtopics

    path("login/", views.login_view, name="login"), # login page
    path("signup/", views.signup_view, name="signup"), # signup page
    path("logout/", views.logout_view, name="logout"),
    # path("<slug:slug>/", views.user_dashboard, name="user_dashboard"),
]