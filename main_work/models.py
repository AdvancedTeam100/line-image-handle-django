from django.db import models

# Create your models here.
class Upload_image(models.Model):
    display_image = models.FileField()
    def __str__(self):
        return self.display_image