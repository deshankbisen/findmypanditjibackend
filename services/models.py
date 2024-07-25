# services/models.py
from django.db import models

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