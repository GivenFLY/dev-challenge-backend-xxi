import uuid

from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=512)
    points = models.JSONField(default=list)

    candidate_labels = models.JSONField(default=list)

    def __str__(self):
        return self.title

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.candidate_labels = [self.title]
        if self.points:
            self.candidate_labels.extend(self.points)
        super().save(*args, force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = "Categories"
