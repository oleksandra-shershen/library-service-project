from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.schemas import UserSchema
from user.serializers import UserSerializer

User = get_user_model()


@method_decorator(name="create", decorator=UserSchema.create)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = ()


@method_decorator(name="manage_user_schema", decorator=UserSchema.manage_user_schema)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = ()

    def get_object(self):
        return self.request.user


@method_decorator(name="save_chat_id_schema", decorator=UserSchema.save_chat_id_schema)
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
