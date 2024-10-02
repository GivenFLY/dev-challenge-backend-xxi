from django.contrib import admin

from categories.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "point_amount")
    search_fields = ("title",)
    readonly_fields = ("candidate_labels",)

    def point_amount(self, obj):
        return len(obj.points)
