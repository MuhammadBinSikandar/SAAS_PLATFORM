from django.db import models

# Create your models here.
class PageVisit(models.Model):
    # db -> table
    # id -> hidden -> primary key -> autofield
    path =  models.TextField(null = True, blank=True) #column
    timestamp =  models.DateTimeField(auto_now_add=True) #columns

    pass 