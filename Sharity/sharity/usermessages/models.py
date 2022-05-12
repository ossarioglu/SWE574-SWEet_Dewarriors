from django.db import models

# Create your models here.
class UserMessage(models.Model):
    message_to = models.ManyToManyField('member.Profile', related_name='recipients')
    message_from = models.ForeignKey('member.Profile', related_name='sender', on_delete=models.CASCADE)
    child = models.ForeignKey('self', null=True, related_name='parent', on_delete=models.SET_NULL)
    subject = models.CharField(max_length=100, null=True, blank=True)
    body = models.TextField()
    is_read_by = models.ManyToManyField('member.Profile', related_name='seen')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def get_all_children(self):
        r = []
        child_ = self.child
        while child_ is not None:
            r.append(child_)
            child_ = child_.child
        return r

class UserInbox(models.Model):
    owner = models.ForeignKey('member.Profile', related_name='inbox', on_delete=models.CASCADE)
    content = models.ManyToManyField(UserMessage, related_name='inbox_content')

    def __str__(self):
        return self.owner.user.username