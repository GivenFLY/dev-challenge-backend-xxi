from rest_framework import serializers

from calls.models import Call


class CallCreateSerializer(serializers.Serializer):
    audio_url = serializers.URLField()


class CallCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ["id"]


class CallDetailSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Call
        fields = ["id", "name", "location", "emotional_tone", "text", "categories"]
