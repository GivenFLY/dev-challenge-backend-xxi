from loguru import logger
from rest_framework import generics, status
from rest_framework.response import Response

from calls.serializers import CallCreateSerializer
from categories.serializers import (
    CategoryListSerializer,
    CategoryCreateUpdateSerializer,
)
from categories.models import Category
from categories.tasks import process_zero_shot_classification_response


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CategoryListSerializer
        else:
            return CategoryCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        result_serializer = CategoryListSerializer(serializer.instance)
        return Response(
            result_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(CategoryListSerializer(instance).data)

    def put(self, request, *args, **kwargs):
        kwargs["partial"] = True

        return self.update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ZeroShotClassificationWebhookAPIView(generics.GenericAPIView):
    serializer_class = CallCreateSerializer  # Dummy serializer

    def post(self, request, *args, **kwargs):
        call_id = request.data.get("call_id")
        result = request.data.get("result")

        if not call_id or not result:
            logger.error("Invalid webhook data")
            return Response(status=status.HTTP_204_NO_CONTENT)

        process_zero_shot_classification_response.delay(call_id, result)

        return Response(status=status.HTTP_200_OK)
