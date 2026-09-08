from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Doctor, Patient, PatientDoctorMapping
from .serializers import DoctorSerializer, MappingSerializer, PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Doctor.objects.all().order_by("name")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.created_by_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update doctors you created.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete doctors you created.")
        instance.delete()


class MappingViewSet(viewsets.ModelViewSet):
    serializer_class = MappingSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(patient__created_by=self.request.user).select_related("patient", "doctor")

    def retrieve(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs["pk"], created_by=request.user)
        mappings = self.get_queryset().filter(patient=patient)
        return Response(self.get_serializer(mappings, many=True).data)


class PatientDoctorsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, id=patient_id, created_by=request.user)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related("doctor")
        return Response(MappingSerializer(mappings, many=True, context={"request": request}).data)
