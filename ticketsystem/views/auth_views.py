from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from ..models import User
from ..serializers.auth_serializers import TicketScannerTokenObtainPairSerializer, UserTokenObtainPairSerializer, RegisterSerializer
# ====================================================================================================
# Authentication API
# ====================================================================================================
class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer

class TicketScannerTokenObtainPairView(TokenObtainPairView):
    serializer_class = TicketScannerTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer