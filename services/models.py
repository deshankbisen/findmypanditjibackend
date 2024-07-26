# services/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class Panditji(models.Model):
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100)
    experience = models.PositiveIntegerField()
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    document = models.FileField(upload_to='documents/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Booking(models.Model):
    user_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    pooja_type = models.CharField(max_length=100)
    poojan_samagri = models.BooleanField(default=False)
    panditji = models.ForeignKey('PanditJi', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('panditji', 'date', 'time')

    def __str__(self):
        return f"Booking for {self.user_name} with {self.panditji} on {self.date} at {self.time}"
    
class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, mobile_number, otp=None, **extra_fields):
        if not mobile_number:
            raise ValueError('The Mobile Number field must be set')
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            mobile_number=mobile_number,
            otp=otp,
            **extra_fields
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, mobile_number, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(first_name, last_name, mobile_number, **extra_fields)

class User(AbstractBaseUser):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.mobile_number