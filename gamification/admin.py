from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Institution, StudentProfile, TeacherProfile, Organization,
    GameTopic, Game, GameAttempt, TaskSubmission,
    EcoPoint, Badge, UserBadge, LoginHistory,Category, SubTopic,QuizOption,QuizQuestion,PuzzleOption,Puzzle
)

class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 1

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "subtopic", "difficulty", "created_at")
    search_fields = ("text", "subtopic__name")
    inlines = [QuizOptionInline]


class PuzzleOptionInline(admin.TabularInline):
    model = PuzzleOption
    extra = 1

@admin.register(Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
    list_display = ("title", "subtopic", "difficulty", "created_at")
    search_fields = ("title", "subtopic__name")
    inlines = [PuzzleOptionInline]

class SubTopicInline(admin.TabularInline):  
    model = SubTopic
    extra = 1   

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "grade_min", "grade_max", "created_at")
    search_fields = ("name",)
    inlines = [SubTopicInline]   

@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    search_fields = ("name", "category__name")


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role", "contact_no", "dob", "address")}),
    )
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "role")



class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    extra = 0


class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    extra = 0


 
class CustomUserAdmin(UserAdmin):
    inlines = [StudentProfileInline, TeacherProfileInline]


# -----------------------------
# Model Registrations
# -----------------------------
admin.site.register(User, CustomUserAdmin)
admin.site.register(Institution)
admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
admin.site.register(Organization)
admin.site.register(GameTopic)
admin.site.register(Game)
admin.site.register(GameAttempt)
admin.site.register(TaskSubmission)
admin.site.register(EcoPoint)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(LoginHistory)
