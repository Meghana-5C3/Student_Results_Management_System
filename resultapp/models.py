from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django import forms

# ---------------------------
# CLASS MODEL
# ---------------------------
class Class(models.Model):
    class_name = models.CharField(max_length=100)  # Full name (e.g., "CSE 2nd Year B")
    department = models.CharField(
        max_length=50,
        choices=[
            ('CSE', 'Computer Science'),
            ('ECE', 'Electronics'),
            ('EEE', 'Electrical'),
            ('MECH', 'Mechanical'),
            ('CIVIL', 'Civil'),
            ('CS', 'Cyber Security'),
        ]
    )
    year = models.PositiveSmallIntegerField(
        choices=[(1, 'I Year'), (2, 'II Year'), (3, 'III Year'), (4, 'IV Year')]
    )
    semester = models.PositiveSmallIntegerField(
        choices=[(1, 'I Semester'), (2, 'II Semester')]
    )
    section = models.CharField(max_length=5)  # e.g., "A"
    academic_session = models.CharField(max_length=20)  # e.g., "2024-2025"
    remarks = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.department} ({self.section})"


# ---------------------------
# SUBJECT MODEL
# ---------------------------
class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    subject_type = models.CharField(
        max_length=20,
        choices=[('THEORY', 'Theory'), ('LAB', 'Lab'), ('PROJECT', 'Project')],
        default='THEORY'
    )
    credits = models.PositiveSmallIntegerField(default=3)
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="subjects")
    department = models.CharField(max_length=50, default="Temp")
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.assigned_class:
            self.department = self.assigned_class.department
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject_name} ({self.subject_code})"


# ---------------------------
# STUDENT MODEL
# ---------------------------
class Student(models.Model):
    roll_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female'),('Other','Other')])
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="students")
    admission_year = models.CharField(max_length=9, default="2024-2025")
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.roll_number} - {self.full_name}"


# ---------------------------
# SUBJECT COMBINATION MODEL
# ---------------------------
class SubjectCombination(models.Model):
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="subject_combinations")
    subjects = models.ManyToManyField(Subject, related_name="combinations")
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        subjects = ", ".join([s.subject_code for s in self.subjects.all()[:5]])
        return f"{self.student_class} - {subjects}" if subjects else f"{self.student_class}"


# ---------------------------
# RESULT MODEL
# ---------------------------
class Result(models.Model):
    SEMESTER_CHOICES = [
        (1, 'I Semester'),
        (2, 'II Semester'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="results")
    subject_combination = models.ForeignKey(SubjectCombination, on_delete=models.CASCADE, related_name="results")
    internal_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    external_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)        
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES, default=1)  # NEW

    total_marks = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    grade = models.CharField(max_length=2, blank=True, null=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_marks = round((self.internal_marks or Decimal(0)) + (self.external_marks or Decimal(0)), 2)


        # Grade Calculation
        if self.total_marks >= 90:
            self.grade = "A+"
        elif self.total_marks >= 80:
            self.grade = "A"
        elif self.total_marks >= 70:
            self.grade = "B"
        elif self.total_marks >= 60:
            self.grade = "C"
        elif self.total_marks >= 50:
            self.grade = "D"
        else:
            self.grade = "F"

        super().save(*args, **kwargs)

    @property
    def status(self):
        """Returns Pass or Fail based on grade or marks."""
        return "Pass" if self.grade != "F" else "Fail"

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.subject_name} ({self.total_marks})"


# ---------------------------
# NOTICE MODEL
# ---------------------------
class Department(models.TextChoices):
    CSE = 'CSE', 'Computer Science'
    ECE = 'ECE', 'Electronics'
    MECH = 'MECH', 'Mechanical'
    CIVIL = 'CIVIL', 'Civil'
    ALL = 'ALL', 'All Departments'

class Notice(models.Model):
    title = models.CharField(max_length=200)
    content= models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    attachment = models.FileField(upload_to='notice_attachments/', blank=True, null=True)
    department = models.CharField(max_length=10, choices=Department.choices, default=Department.ALL)
    target_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=[('High','High'),('Medium','Medium'),('Low','Low')], default='Medium')
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', '-publish_date']

    def __str__(self):
        return self.title


# ---------------------------
# MIGRATION MODEL
# ---------------------------
class Migration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='migrations')
    old_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name='old_class_migrations')
    new_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_class_migrations')
    migration_date = models.DateField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        old = self.old_class or "N/A"
        new = self.new_class or "N/A"
        return f"{self.student.full_name} migrated from {old} to {new}"







class NoticeForm(forms.ModelForm):
    publish_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    expiry_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))

    class Meta:
        model = Notice
        fields = ['title', 'content', 'attachment', 'department', 'target_class', 'priority', 'publish_date', 'expiry_date']
        widgets = {
            'content': forms.Textarea(attrs={'rows':5, 'placeholder':'Enter notice content...'}),
        }