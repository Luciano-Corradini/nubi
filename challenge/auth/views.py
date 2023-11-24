from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from auth.authentication import TokenHandler
from auth.serializers import UserSerializer, RegisterSerializer


class Login(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        login_serializer = self.serializer_class(data=request.data, context={ 'request': request })
        login_serializer.is_valid(raise_exception=True)

        user = login_serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        _, token = TokenHandler.expiration_handle(token, is_login=True)
        user_serializer = UserSerializer(user)
        
        return Response(
            { 'token': token.key, 'user': user_serializer.data },
            status=status.HTTP_200_OK
        )

class Register(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
