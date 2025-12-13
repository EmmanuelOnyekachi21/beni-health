from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsProvider
from apps.enrollees.models import Enrollees
from django.db.models import Q


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsProvider])
def verify_user(request):
    """
    Verify patient coverage and eligibility.
    
    Accepts any combination of:
    - phone
    - email
    - enrollee_id
    - first_name + last_name
    
    Returns coverage status, plan details, and balance.
    """
    phone = request.get('phone', None)
    email = request.get('email', None)
    enrollee_id = request.get('enrollee_id', None)
    first_name = request.get('first_name', None)
    last_name = request.get('last_name', None)

    # Validating that at least one search parameter was provided
    if not phone and not email and not enrollee_id and not (first_name and last_name):
        return Response({
            'error': 'At least one search parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # ---------------------------
    # Build flexible Q query
    # ---------------------------
    query = Q()

    if phone:
        query |= Q(contact_phone__icontains=phone)
    if email:
        query |= Q(contact_email__icontains=email)
    if enrollee_id:
        query |= Q(enrollee_id__icontains=enrollee_id)
    if first_name and last_name:
        query |= Q(first_name__icontains=first_name) & Q(last_name__icontains=last_name)
    
    enrollee = Enrollees.objects.filter(query).first()

    
    if not enrollee:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # -----------------------------
    # Check coverage
    # -----------------------------
    if not enrollee.is_coverage_active():
        return Response(
            {"status": "inactive", "message": "Coverage is not active"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # -----------------------------
    # Return coverage details
    # -----------------------------
    annual_cap = enrollee.plan.annual_cap
    used_amount = 0
    remaining = annual_cap - used_amount
    
    # ---------------------------
    # TASK 7: Construct response
    # ---------------------------
    response_data = {
        "status": "active",
        "enrollee": {
            "id": str(enrollee.id),
            "enrollee_id": enrollee.enrollee_id,
            "name": f"{enrollee.first_name} {enrollee.last_name}",
            "dob": enrollee.dob,
            "phone": enrollee.phone,
            "email": enrollee.email,
        },
        "plan": {
            "name": enrollee.plan.name,
            "annual_cap": float(annual_cap),
        },
        "balance": {
            "annual_cap": float(annual_cap),
            "used": float(used_amount),
            "remaining": float(remaining),
            "percentage_used": (used_amount / annual_cap * 100) if annual_cap > 0 else 0
        },
        "coverage": {
            "start_date": enrollee.coverage_start,
            "end_date": enrollee.coverage_end,
            "days_remaining": (enrollee.coverage_end - timezone.now().date()).days
        }
    }

    return Response(response_data, status=status.HTTP_200_OK)


