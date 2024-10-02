from rest_framework import serializers

from categories.models import Category


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "points"]


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["title", "points"]

    def validate(self, attrs):
        if len(attrs) > 2:
            raise serializers.ValidationError("Only title and points are allowed.")

        if not isinstance(attrs.get("points"), list):
            raise serializers.ValidationError("Points must be a list.")

        for point in attrs.get("points", []):
            if not isinstance(point, str):
                raise serializers.ValidationError("Points must be list of strings.")

        return attrs
