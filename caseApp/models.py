from django.db import models

class Case(models.Model):
    facts = models.TextField()
    issues = models.TextField()
    arguments = models.TextField()
    reference_materials = models.TextField()
    # Add any other fields you need
