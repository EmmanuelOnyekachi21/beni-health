from rest_framework import serializers
from apps.enrollees.models import Enrollees
from apps.plans.serializers import PlanSerializer


class EnrolleeSerializer(serializers.ModelSerializer):
    """
    Serializer for Enrollee model
    """
    plan_details = PlanSerializer(
        source="plan",
        read_only=True
    )
    class Meta:
        model = Enrollees
        fields = [
            'id', 'enrollee_id', 'first_name', 'last_name', 'dob',
            'gender', 'phone', 'email', 'national_id', 'address',
            'employer', 'plan', 'plan_details', 'status',
            'coverage_start', 'coverage_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'enrollee_id', 'created_at', 'updated_at']
    
    def get_is_active(self, obj):
        return obj.is_coverage_active()


class EnrolleeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to create an Enrollee.
    """
    class Meta:
        model = Enrollees
        fields = [
            'first_name', 'last_name', 'dob', 'gender', 'phone',
            'email', 'national_id', 'address', 'plan',
            'status', 'coverage_start', 'coverage_end'
        ]
    
    def create(self, validated_data):
        """
        Create Enrollee.
        """

        # Get request from serializer context.
        request = self.context.get('request')
        employer = request.user.profile.employer_profile
        validated_data['employer']  = employer
        return Enrollees.objects.create(**validated_data)

