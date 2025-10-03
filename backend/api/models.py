"""
This script MUST be run first before running any other code.
It only needs to be run once to configure the tables in the cloud database.
For local databases, it should be run regularly whenever the migration has been changed.

Run these commands in your terminal:
1. python manage.py makemigrations
2. python manage.py migrate
"""
import uuid
from django.db import models
from recurrence.fields import RecurrenceField
from django.contrib.auth.models import AbstractUser

def user_directory_path(instance, filename):
    return f'user_{instance.user.user_id}/img/{filename}'

def report_file_path(instance, filename):
    return f'user_{instance.user.user_id}/pdfs/{filename}'

# AbstractUser already provides username, password, and email
class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='api_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='api_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    user_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_img = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    is_automated = models.BooleanField(default=False)
    auto_frequency = RecurrenceField(blank=True)
    font_size = models.IntegerField(default=12) #TODO: check and edit default value

    def __str__(self):
        return f"Profile for User {self.user.username}"

class Questionnaire(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    org_name = models.CharField(max_length=300)
    email_domain = models.CharField(max_length=100)
    website_domain = models.CharField(max_length=100)
    external_ip = models.CharField(max_length=100)
    require_mfa_email = models.BooleanField()
    require_mfa_sensitive_data = models.BooleanField()
    employee_acceptable_use_policy = models.BooleanField()
    training_new_employees = models.BooleanField()
    training_once_per_year = models.BooleanField()

    def __str__(self):
        return f"Questionnaire from User {self.user.username}"

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_id = models.UUIDField(
        primary_key = True,
        default=uuid.uuid4,
        editable=False
    )
    report_name = models.CharField(max_length=300)
    date_created = models.DateTimeField(auto_now_add=True)
    time_started = models.DateTimeField(blank=True, null=True)
    time_completed = models.DateTimeField(blank=True, null=True)
    report_text = models.FileField(upload_to=report_file_path)

    def __str__(self):
        return f"Report {self.report_name} from User {self.user.username}"

class Risk(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    risk_name = models.CharField(max_length=300)
    affected = models.IntegerField(default=0)
    overview_text = models.TextField()
    recommendation_text = models.TextField()
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"Risk {self.risk_name} from Report {self.report.report_name} from User {self.report.user.username}"