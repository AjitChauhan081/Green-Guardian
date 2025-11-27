from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


# -------------------------------
# Custom User Model
# -------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ("school_student", "School Student"),
        ("college_student", "College Student"),
        ("school_teacher", "School Teacher"),
        ("college_teacher", "College Teacher"),
        ("ngo", "NGO"),
        ("government", "Government"),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    contact_no = models.CharField(max_length=15, blank=True)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


# -------------------------------
# Institutions (School / College)
# -------------------------------
class Institution(models.Model):
    TYPE_CHOICES = [("School", "School"), ("College", "College")]
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    

    def __str__(self):
        return f"{self.name} ({self.type})"


# -------------------------------
# Students
# -------------------------------
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    enrollment_no = models.CharField(max_length=50)
    grade = models.IntegerField(null=True, blank=True)   # 1-12 (for school)
    stream = models.CharField(max_length=100, blank=True)  # Science/Arts (if grade > 10)
    current_year = models.IntegerField(null=True, blank=True)  # For college
    course = models.CharField(max_length=100, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    gender_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    gender = models.CharField(max_length=7, choices=gender_CHOICES, default="male")

    def __str__(self):
        return f"Student: {self.user.username}"


# -------------------------------
# Teachers
# -------------------------------
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    teacher_id = models.CharField(max_length=50)
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    gender_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    gender = models.CharField(max_length=7, choices=gender_CHOICES, default="male")

    def __str__(self):
        return f"Teacher: {self.user.username}"


# -------------------------------
# Organizations (NGO / Government)
# -------------------------------
class Organization(models.Model):
    ORG_CHOICES = [("NGO", "NGO"), ("Government", "Government")]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ORG_CHOICES)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    website = models.URLField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type})"


# -------------------------------
# Game Topics
# -------------------------------
class GameTopic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# -------------------------------
# Games
# -------------------------------
class Game(models.Model):
    GAME_TYPE_CHOICES = [
        ("quiz", "Quiz"),
        ("puzzle", "Puzzle"),
        ("mini_game", "Mini Game"),
        ("real_world_task", "Real World Task"),
    ]
    DIFFICULTY_CHOICES = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]

    title = models.CharField(max_length=255)
    description = models.TextField()
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES)
    grade_min = models.IntegerField(null=True, blank=True)
    grade_max = models.IntegerField(null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, blank=True)
    topic = models.ForeignKey(GameTopic, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.game_type})"


# -------------------------------
# Game Attempts (for quizzes, puzzles, mini-games)
# -------------------------------
class GameAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField()
    accuracy = models.FloatField(null=True, blank=True)
    time_taken = models.IntegerField(null=True, blank=True)  # in seconds
    progress = models.FloatField(null=True, blank=True)      # percentage
    attempt_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"


# -------------------------------
# Task Submissions (Real World Tasks)
# -------------------------------
class TaskSubmission(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, limit_choices_to={"game_type": "real_world_task"},null=True, blank=True )
    submission = models.TextField()  # proof URL or description
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="verified_tasks")
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Task by {self.user.username}"


# -------------------------------
# EcoPoints (only from verified tasks)
# -------------------------------
class EcoPoint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.OneToOneField(TaskSubmission, on_delete=models.CASCADE,null=True,blank=True)
    points = models.IntegerField()
    awarded_at = models.DateTimeField(auto_now_add=True)
    is_daily = models.BooleanField(default=False)  # 👈 new field to mark daily login rewards


    def __str__(self):
        reward_type = "Daily Login" if self.is_daily else "Task"
        return f"{self.user.username} - {self.points} pts ({reward_type})"


# -------------------------------
# Badges
# -------------------------------
class Badge(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    unlock_criteria = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# -------------------------------
# User Badges
# -------------------------------
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


# -------------------------------
# Login History
# -------------------------------
class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"


# -------------------------------
# Categories
# -------------------------------
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)         # e.g. "Greenhouse Gas Emissions"
    description = models.TextField(blank=True)
    grade_min = models.IntegerField(null=True, blank=True)       # Minimum grade eligible
    grade_max = models.IntegerField(null=True, blank=True)       # Maximum grade eligible
    godot_game_file = models.FileField(upload_to="games/", blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# -------------------------------
# Subtopics
# -------------------------------
class SubTopic(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subtopics")
    name = models.CharField(max_length=255)                      # e.g. "Methane"
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category.name} – {self.name}"


# -------------------------------
# Quiz
# -------------------------------
class QuizQuestion(models.Model):
    subtopic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, related_name="quiz_questions")
    text = models.TextField()
    difficulty = models.CharField(
        max_length=10,
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        default="easy",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

# -------------------------------
# Quiz Options
# -------------------------------

class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'correct' if self.is_correct else 'wrong'})"


# -------------------------------
# Puzzle
# -------------------------------
class Puzzle(models.Model):
    subtopic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, related_name="puzzles")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    difficulty = models.CharField(
        max_length=10,
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        default="easy",
    )
    media = models.FileField(upload_to="puzzles/", blank=True, null=True)  # image or file
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# -------------------------------
# Puzzle Options
# -------------------------------

class PuzzleOption(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'correct' if self.is_correct else 'wrong'})"
