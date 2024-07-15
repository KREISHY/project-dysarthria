from rest_framework.viewsets import ModelViewSet, GenericViewSet

from api_v0.permissions import IsMemberOfGroupOrAdmin
from project.settings import DEBUG as debug_settings
from rest_framework import generics, mixins, views, permissions, viewsets

from testing.models.test import Exercise, ExerciseToTest, ResponseExercise, ExerciseType
from testing.serializers.testing import ExerciseSerializer, ResponseExerciseSerializer, \
    PublicDetailSerializer, ExerciseToTestSerializer, ExerciseTypeSerializer


class ExerciseTypeViewSet(viewsets.ModelViewSet):
    queryset = ExerciseType.objects.all()
    serializer_class = ExerciseTypeSerializer


class ExerciseModelViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           GenericViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer


class ExerciseToTestModelViewSet(mixins.CreateModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 mixins.ListModelMixin,
                                 GenericViewSet):
    queryset = ExerciseToTest.objects.all()
    serializer_class = ExerciseToTestSerializer


class ResponseExerciseModelViewSet(mixins.CreateModelMixin,
                                   mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   mixins.ListModelMixin,
                                   GenericViewSet):
    queryset = ResponseExercise.objects.all()
    serializer_class = ResponseExerciseSerializer
    permission_classes = [
        permissions.AllowAny
    ]


