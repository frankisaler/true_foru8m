from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def get_absolute_url(self):
        """Returns the url to access a particular user instance."""
        return reverse('user-detail', args=[str(self.id)])
