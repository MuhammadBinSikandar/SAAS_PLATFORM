from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    strip_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"
    
    def save(self, *args, **kwargs):
        self.strip_id = "some-random-id"
        super().save(*args, **kwargs)