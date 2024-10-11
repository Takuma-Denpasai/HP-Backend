from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet

from .models import UserData
from .serializers import LoginSerializer


class LoginViewSet(ViewSet):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["POST"])
    def login(self, request):
        """ユーザのログイン"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse(
                data={"status": False, "msg": "ユーザーネームまたはパスワードが間違っています"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            login(request, user)
            # ユーザー情報を含むレスポンスを返す
            return JsonResponse(
                data={
                    "status": True,
                    "username": user.username,
                    "email": user.email,
                }
            )

    @action(methods=["GET"], detail=False)
    def logout(self, request):
        """ユーザのログアウト"""
        logout(request)
        return JsonResponse(data={"status": True, "msg": "ログアウトしました"})
