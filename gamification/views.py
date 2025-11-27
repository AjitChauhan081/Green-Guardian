
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from .models import User, StudentProfile, TeacherProfile, Organization, Institution,StudentProfile, EcoPoint, UserBadge, GameAttempt, TaskSubmission,Category,SubTopic
from django.utils.timezone import localdate,now
from django.db.models import Sum





def home(request):
    if request.user.is_authenticated:
        role = request.user.role
        if role in ["school_student", "college_student"]:
            return redirect("student_dashboard", slug=request.user.slug)
            # return render(request, "dashboards\student_dashboard.html", slug=request.user.slug)
        elif role in ["school_teacher", "college_teacher"]:
            return render(request, "dashboards/teacher_dashboard.html", {"user": request.user})
        elif role in ["ngo", "government"]:
            return render(request, "dashboards\ngo_dashboard.html")
        else:
            return render(request, "dashboards\dashboard.html")
    return render(request, "home.html") 

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        # Authenticate
        user = authenticate(request, username=username, password=password)

        if user is not None and user.role == role:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username} ({user.role})!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username, password, or role.")

    return render(request, "login.html")

def logout_view(request):
    logout(request)  
    request.session.flush() 
    messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def student_dashboard(request, slug):
    user = get_object_or_404(User, slug=slug, role__in=["school_student", "college_student"])
    student_profile = StudentProfile.objects.get(user=user)
    institution = student_profile.institution
    today = localdate()
    already_rewarded = EcoPoint.objects.filter(
    user=user,
    is_daily=True,
    awarded_at__date=today
    ).exists()
    
    if not already_rewarded:
        EcoPoint.objects.create(
            user=user,
            points=1,
            is_daily=True,
            awarded_at=today
            # 👈 clearly marks it
        )
        messages.success(request, "+1 Eco Point for Daily Login!")

   
    # try:
    #     student_profile = StudentProfile.objects.get(user=user)
    #     institution = student_profile.institution
    # except StudentProfile.DoesNotExist:
    #     student_profile = None
    #     institution = None

    total_points = EcoPoint.objects.filter(user=user).aggregate(Sum("points"))["points__sum"] or 0
    submissions = TaskSubmission.objects.filter(user=user).select_related("game").order_by("-submitted_at")[:5]

    leaderboard = []
    if institution:
        leaderboard = (
            EcoPoint.objects.filter(user__studentprofile__institution=institution)
            .values("user__username")
            .annotate(total=Sum("points"))
            .order_by("-total")[:10]
        )

    categories = Category.objects.all()

    category_id = request.GET.get("category")
    if category_id:
        try:
            category_selected = Category.objects.get(id=category_id)
            subtopics = SubTopic.objects.filter(category=category_selected)
        except Category.DoesNotExist:
            category_selected = None
            subtopics = None
    else:
        category_selected = None
        subtopics = None
        
    return render(request, "dashboards/student_dashboard.html", {
        "user": user,
        "categories": categories,
        "subtopics": subtopics,
        "recent_attempts": GameAttempt.objects.filter(user=user).select_related("game").order_by("-attempt_date")[:5],
        "total_points": total_points,
        "student_profile": student_profile,
        "institution": institution,
        "badges": UserBadge.objects.filter(user=user).select_related("badge"),
        "submissions": submissions,
        "leaderboard": leaderboard,
        "category_selected": category_selected,
    })
    
def explore_subtopics(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subtopics = SubTopic.objects.filter(category=category)
    return render(request, "dashboards/subtopics.html", {
        "category": category,
        "subtopics": subtopics,
    })
    
# @login_required
# def student_dashboard(request, slug):
#     user = get_object_or_404(User, slug=slug, role__in=["school_student", "college_student"])

#     # Ensure profile exists
#     try:
#         student_profile = StudentProfile.objects.get(user=user)
#         institution = student_profile.institution
#     except StudentProfile.DoesNotExist:
#         student_profile = None
#         institution = None

#     total_points = EcoPoint.objects.filter(user=user).aggregate(Sum("points"))["points__sum"] or 0
#     submissions = TaskSubmission.objects.filter(user=user).select_related("game").order_by("-submitted_at")[:5]

#     leaderboard = []
#     if institution:
#         leaderboard = (
#             EcoPoint.objects.filter(user__studentprofile__institution=institution)
#             .values("user__username")
#             .annotate(total=Sum("points"))
#             .order_by("-total")[:10]
#         )

#     return render(request, "dashboards/student_dashboard.html", {
#         "user": user,
#         "categories": Category.objects.all(),
#         "subtopics": SubTopic.objects.filter(category=category) if category_selected else None,
#         "recent_attempts": GameAttempt.objects.filter(user=user).select_related("game").order_by("-attempt_date")[:5],
#         "total_points": EcoPoint.objects.filter(user=user).aggregate(total=Sum("points"))["total"] or 0,
#         "student_profile": student_profile,
#         "institution": institution,
#         "total_points": total_points,
#         "badges": UserBadge.objects.filter(user=user).select_related("badge"),
#         "submissions": submissions,
#         "leaderboard": leaderboard,
#     })
@login_required
def teacher_dashboard(request,slug):
    # You can pass data to the template here if needed
    user = get_object_or_404(User, slug=slug, role__in=["school_teacher", "college_teacher"])
    context = {
        "user": user,
        
    }
    return render(request, "dashboards/teacher_dashboard.html", context)

def signup_view(request):
    if request.method == "POST":
        role = request.POST.get("role")
        gender = request.POST.get("gender")
        username = request.POST.get("username")
        email = request.POST.get("email")
        contact_no = request.POST.get("contact_no")
        dob = request.POST.get("dob")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        address = request.POST.get("address")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "signup.html")

        # Create user
        user = User(
            username=username,
            email=email,
            contact_no=contact_no,
            dob=dob if dob else None,
            role=role,
            first_name=first_name,
            last_name=last_name,
            address=address,
        )
        user.set_password(password1)
        user.save()

        if role in ["school_student", "college_student"]:
            enrollment_no = request.POST.get("enrollment_no")
            grade = request.POST.get("grade")
            stream = request.POST.get("stream")
            current_year = request.POST.get("current_year")
            course = request.POST.get("course")
            field_of_study = request.POST.get("field_of_study")
            institution_value = request.POST.get("institution")

            if institution_value == "other":
                inst_name = request.POST.get("other_school_name")
                inst_state = request.POST.get("other_school_state")
                inst_city = request.POST.get("other_school_city")

                institution = Institution.objects.create(
                    name=inst_name,
                    state=inst_state,
                    city=inst_city,
                    type="School" if "school" in request.POST.get("role") else "College"
                )
            else:
                institution = Institution.objects.get(id=institution_value)

          

            StudentProfile.objects.create(
                user=user,
                gender=gender,
                institution=institution,
                enrollment_no=enrollment_no,
                grade=grade if grade else None,
                stream=stream,
                current_year=current_year if current_year else None,
                course=course,
                field_of_study=field_of_study,
            )

        elif role in ["school_teacher", "college_teacher"]:
            # institution_name = request.POST.get("institution")
            teacher_id = request.POST.get("teacher_id")
            designation = request.POST.get("designation")
            department = request.POST.get("department")
            institution_value = request.POST.get("institution")

            if institution_value == "other":
                inst_name = request.POST.get("other_school_name")
                inst_state = request.POST.get("other_school_state")
                inst_city = request.POST.get("other_school_city")

                institution = Institution.objects.create(
                    name=inst_name,
                    state=inst_state,
                    city=inst_city,
                    type="School" if "school" in request.POST.get("role") else "College"
                )
            else:
                institution = Institution.objects.get(id=institution_value)

          

            TeacherProfile.objects.create(
                user=user,
                gender=gender,
                institution=institution,
                teacher_id=teacher_id,
                designation=designation,
                department=department,
            )

        elif role in ["ngo", "government"]:
            org_name = request.POST.get("org_name")
            org_type = request.POST.get("org_type")
            contact_person = request.POST.get("contact_person")
            website = request.POST.get("website")
            state = request.POST.get("state")
            city = request.POST.get("city")

            Organization.objects.create(
                name=org_name,
                type=org_type.capitalize(),  # "NGO" / "Government"
                contact_person=contact_person,
                email=email,
                website=website,
                address=address,
                state=state,
                city=city,
            )
        print(user,
                gender,
                institution,
                enrollment_no,
                grade,
                stream,
                current_year,
                course,
                field_of_study,)
        messages.success(request, "Account created! Please log in.")
        return redirect("login")
    else:
        institutions = Institution.objects.all()
        return render(request, "signup.html", {"institutions": institutions})

    return render(request, "signup.html")


@login_required
def user_dashboard(request, slug):
    user_profile = get_object_or_404(User, slug=slug)

    # Only allow self-access (or extend for teacher/admin to see students)
    if request.user != user_profile:
        return redirect("home")

    role = user_profile.role

    if role in ["school_student", "college_student"]:
        template = "dashboards/student_dashboard.html"
    elif role in ["school_teacher", "college_teacher"]:
        template = "dashboards/teacher_dashboard.html"
    elif role == "ngo":
        template = "dashboards/ngo_dashboard.html"
    elif role == "government":
        template = "dashboards/government_dashboard.html"
    else:
        template = "dashboards/generic_dashboard.html"

    return render(request, template, {"user": user_profile})