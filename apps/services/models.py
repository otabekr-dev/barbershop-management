from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()


    def __str__(self):
        return f'{self.id}.{self.name}'