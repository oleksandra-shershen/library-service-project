from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer

User = get_user_model()


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = ()


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = ()

    def get_object(self):
        return self.request.user


class SaveChatIdView(APIView):

    def post(self, request):
        email = request.data.get("email")
        chat_id = request.data.get("chat_id")

        user = User.objects.filter(email=email).first()
        if user:
            user.telegram_chat_id = chat_id
            user.save()
            return Response(
                {"message": "Chat ID saved successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
