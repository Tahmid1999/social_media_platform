from djongo import models
import uuid 
from datetime import datetime

class Posts(models.Model):
    _id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orginal_creator_user_id = models.CharField(max_length=255)
    creator_user_id = models.CharField(max_length=255)
    text = models.TextField()
    images = models.JSONField(default=list)
    likes = models.JSONField(default=list)
    comments = models.JSONField(default=list)
    kewords = models.JSONField(default=list)
    is_shared = models.BooleanField(default=False)
    share_count = models.IntegerField(default=0)
    original_post_id = models.CharField(max_length=255, null=True)
    created_dateTime = models.DateTimeField(default=datetime.now)

    def get_formatted_data(self):
        formatted_data = {
            '_id': self._id,
            'orginal_creator_user_id': self.orginal_creator_user_id,
            'text': self.text,
            'images': self.images,
            'likes_count': len(self.likes),
            'comments_count': len(self.comments),
            #'shares_count': len(self.shares),
            'latest_comment': self.comments[-1] if len(self.comments) > 0 else None,
            'kewords': self.kewords,
            'created_dateTime': self.created_dateTime
        }
        return formatted_data