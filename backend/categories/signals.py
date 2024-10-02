from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache

from core.consts import (
    CANDIDATE_LABEL_CACHE_KEY,
    CATEGORY_POINTS_CACHE_KEY,
    CATEGORIES_CACHE_KEY,
)
from .models import Category
from .tasks import (
    send_zero_shot_classification_request_for_specific_category,
    send_zero_shot_classification_request_for_affected_calls,
)


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def clear_category_cache(sender, **kwargs):
    """
    Signal to clear the cached data when a Category object is saved or deleted.
    """
    cache.delete(CATEGORIES_CACHE_KEY)
    cache.delete(CANDIDATE_LABEL_CACHE_KEY)
    cache.delete(CATEGORY_POINTS_CACHE_KEY)


@receiver(pre_save, sender=Category)
def pre_save_category(sender, instance, **kwargs):
    # get previous instance if possible
    if instance.pk:
        instance._old_instance = Category.objects.get(pk=instance.pk)

    if instance._old_instance and sorted(instance._old_instance.points) != sorted(
        instance.points
    ):
        send_zero_shot_classification_request_for_specific_category.delay(instance.id)


@receiver(post_save, sender=Category)
def post_save_category(sender, instance, **kwargs):
    created = kwargs.get("created", False)

    if created:
        send_zero_shot_classification_request_for_specific_category.delay(instance.id)
