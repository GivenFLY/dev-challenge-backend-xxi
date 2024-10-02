from calls.choices import EMOTIONAL_TONE_LABELS
from categories.models import Category


from django.core.cache import cache

from core.consts import (
    CATEGORY_POINTS_CACHE_KEY,
    CANDIDATE_LABEL_CACHE_KEY,
    CATEGORIES_CACHE_KEY,
)


def get_all_categories():
    """
    Get all categories, with caching.

    :return: Dict of categories
    """

    cache_key = CATEGORIES_CACHE_KEY
    categories = cache.get(cache_key)

    if categories is None:
        categories = {}

        for category in Category.objects.all():
            categories[category.id] = {
                "title": category.title,
                "points": category.points,
            }

        cache.set(cache_key, categories, timeout=300)

    return categories


def get_all_category_points():
    """
    Get all category points for the zero-shot classification, with caching.

    :return: Dict of category points
    """
    cache_key = CATEGORY_POINTS_CACHE_KEY
    points = cache.get(cache_key)

    if points is None:
        points = {}

        for category in Category.objects.all():
            points[category.title] = category.points

        cache.set(cache_key, points, timeout=300)

    return points


def get_all_candidate_labels():
    """
    Get all candidate labels for the zero-shot classification, with caching.

    :return: List of candidate labels
    """
    cache_key = CANDIDATE_LABEL_CACHE_KEY
    labels = cache.get(cache_key)

    if labels is None:
        labels = []
        categories = get_all_category_points()
        for category in categories:
            labels.append(category)
            labels.extend(categories[category])

        labels.extend(list(EMOTIONAL_TONE_LABELS.values()))
        cache.set(cache_key, labels, timeout=300)

    return labels
