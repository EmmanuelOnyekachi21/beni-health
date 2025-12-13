from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsEmployer
from apps.enrollees.models import Enrollees
from apps.enrollees.serializers import EnrolleeSerializer, EnrolleeCreateSerializer
import pandas as pd
from rest_framework.parsers import MultiPartParser
from django.db import transaction
from .utils import read_csv



@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def enrollees_list_create(request):
    """
    GET: List all enrollees for the logged-in employer
    POST: Create new enrollee
    """
    if request.method == "GET":
        enrollees = Enrollees.objects.filter(
            employer=request.user.profile.employer_profile
        )
        serializer = EnrolleeSerializer(enrollees, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = EnrolleeCreateSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            enrollee = serializer.save()
            return Response(EnrolleeSerializer(enrollee).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated, IsEmployer])
def enrollee_detail(request, enrollee_id):
    try:
        enrollee = Enrollees.objects.get(enrollee_id=enrollee_id)
    except Enrollees.DoesNotExist:
        return Response(
            {"error": "Enrollee not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check ownership
    if enrollee.employer != request.user.profile.employer_profile:
        return Response(
            {"error": "Enrollee does not belong to this employer"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        serializer = EnrolleeSerializer(enrollee)
        return Response(serializer.data)
    
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = EnrolleeSerializer(enrollee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        enrollee.status = 'TERMINATED'
        enrollee.save()
        return Response(
            {"message": "Enrollee terminated successfully"},
            status=status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
@parser_classes([MultiPartParser])
def bulk_upload_enrollee(request):
    """
    Upload CSV/Excel file with multiple enrollees
    Expected columns: first_name, last_name, dob, gender, phone, email, plan_id
    """

    file = request.FILES.get('file')
    if not file:
        return Response(
            {"error": "No file uploaded"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Call helper function
    df = read_csv(file)
    
    required_columns = [
        'first_name',
        'last_name',
        'dob',
        'gender',
        'phone',
        'plan_id',
        'email',
        'national_id',
        'address'
    ]
    value = all(column in df.columns for column in required_columns)
    if not value:
        return Response(
            {"error": "File must contain all required columns"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    employer = request.user.profile.employer_profile
    created = 0
    errors = []

    for index, row in df.iterrows():
        try:
            with transaction.atomic():
                first_name = row['first_name']
                last_name = row['last_name']
                dob = row['dob']
                gender = row['gender']
                phone = row['phone']
                email = row['email']
                national_id = row['national_id']
                address = row['address']
                plan = row['plan_id']
                enrollee_status = row['status']
                coverage_start = row['coverage_start']
                coverage_end = row['coverage_end']

                serializer = EnrolleeCreateSerializer(data={
                    'first_name': first_name,
                    'last_name': last_name,
                    'dob': dob,
                    'gender': gender,
                    'phone': phone,
                    'email': email,
                    'national_id': national_id,
                    'address': address,
                    'plan': plan,
                    'status': enrollee_status,
                    'coverage_start': coverage_start,
                    'coverage_end': coverage_end
                }, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    created += 1
                else:
                    errors.append({
                        'row': index + 2,  # +2 for header row and 0-indexing
                        'data': row.to_dict(),
                        'errors': serializer.errors
                    })
        
        except Exception as e:
            errors.append({
                'row': index + 2,
                'error': str(e),
                'data': row.to_dict()
            })
    
    return Response(
        {
            'message': f'Bulk upload completed',
            'total_rows': len(df),
            'created': created,
            'failed': len(errors),
            'errors': errors[:10]  # Return only first 10 errors to avoid huge response
        },
        status=status.HTTP_201_CREATED if created > 0 else status.HTTP_400_BAD_REQUEST
    )
            

            
