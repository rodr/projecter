from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta:
        db_table = "company"
        verbose_name_plural = _("companies")
        
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    company = models.ForeignKey(Company)
    title = models.CharField(max_length=255)

    setup_done = models.BooleanField(default=False)
    
    class Meta:
        db_table = "user_profile"
