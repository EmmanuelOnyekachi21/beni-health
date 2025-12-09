from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .permissions import IsEmployer, IsEmployee


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserProfileSerializer(user.profile).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh(request):
    serializer = TokenRefreshSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    except TokenError as e:
        raise InvalidToken(e.args[0])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get current user's profile.
    """
    serializer = UserProfileSerializer(request.user.profile)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def employer_dashboard(request):
    """
    Get employer dashboard.
    """
    profile = request.user.profile
    employer_data = None
    
    if hasattr(profile, 'employer_profile'):
        try:
            employer_data = {
                "company_name": profile.employer_profile.company_name,
                "number_of_employees": profile.employer_profile.number_of_employees,
                "industry": profile.employer_profile.industry,
            }
        except profile.employer_profile.RelatedObjectDoesNotExist:
            pass
    
    return Response(
        {
            "message": "Welcome to the Employer dashboard",
            "employer": employer_data
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def employee_dashboard(request):
    """
    Get employee dashboard.
    """
    profile = request.user.profile
    employee_data = None
    
    if hasattr(profile, 'employee_profile'):
        try:
            emp_profile = profile.employee_profile
            employee_data = {
                "employee_id": emp_profile.employee_id,
                "department": emp_profile.department,
                "job_title": emp_profile.job_title,
                "employer": emp_profile.employer.company_name if emp_profile.employer else None
            }
        except profile.employee_profile.RelatedObjectDoesNotExist:
            pass
    
    return Response(
        {
            "message": "Welcome to the Employee dashboard",
            "employee": employee_data
        },
        status=status.HTTP_200_OK
    )
