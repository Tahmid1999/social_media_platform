from djongo import models
import uuid 
from datetime import datetime

# Create your models here.
class Connections(models.Model):
    _id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_id = models.CharField(max_length=255)
    receiver_id = models.CharField(max_length=255)
    is_accepted = models.BooleanField(default=False)
    accepted_dateTime = models.DateTimeField(null=True)
    created_dateTime = models.DateTimeField(default=datetime.now)
