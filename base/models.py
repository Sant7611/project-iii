from django.db import models
from django.conf import settings

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        update_kwargs = {'is_deleted':True, 'is_active':False}
        return self.update(update_kwargs)
    
    def hard_delete(self):
        return super().delete()
    
    def restore(self):
        update_kwargs = {'is_deleted':False, 'is_active':True}
        return self.update(update_kwargs)
    
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )  

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s_updated',
        null=True,
        blank=True
    )

    class Meta:
        abstract= True
        ordering = ['-created_at']

    objects = SoftDeleteManager()
    all_objects = models.Manager()
