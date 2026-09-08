from rest_framework import serializers

from .models import Doctor, Patient, PatientDoctorMapping


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ("id", "name", "date_of_birth", "gender", "contact", "address", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ("id", "name", "specialization", "contact", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class MappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "doctor", "assigned_at")
        read_only_fields = ("id", "assigned_at")

    def validate(self, attrs):
        request = self.context["request"]
        patient = attrs.get("patient")
        if patient and patient.created_by_id != request.user.id:
            raise serializers.ValidationError({"patient": "You can only assign doctors to your patients."})
        return attrs
