from django.shortcuts import render
from rest_framework.exceptions import ParseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions, mixins
from users.serializer import RegisterSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView

from users.models import User  # noqa


# Create your views here.
class UserApi(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user



class RegisterApi(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RegisterSerializer
    def post(self, request, *args,  **kwargs):
        print("haha")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User Created Successfully.  Now perform Login to get your token",
        })
