from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from .models import *
from .constant import *
import boto3, random, string, os

# Create your views here.

def healthcheck(request):
  
  return JsonResponse({'health': 'ok'})

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # 誰でもアクセス可能

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'ユーザーが正常に作成されました。'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 追加のクレームを含める場合はここで設定
        token['username'] = user.username
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveImage(request):
    
    if request.method == 'POST':
        
        s3 = boto3.client('s3', 
                          aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        def randomString(n = 30):
            return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(n)])
        
        image = request.FILES.get('file')
        print(image)
        
        while True:
            filename = randomString() + '.' + image.name.split('.')[-1]
            print(filename)
            if not ImageData.objects.filter(image=f'{os.environ.get('AWS_CLOUD_FRONT_URL')}/{filename}').exists():
                break
        
        try:
            s3.put_object(
                Bucket=os.environ.get('AWS_S3_BUCKET'),
                Key=filename,
                Body=image.read(),
                ContentType=image.content_type
            )
            
            ImageData.objects.create(image=f'{os.environ.get('AWS_CLOUD_FRONT_URL')}/{filename}')
            
            return JsonResponse({'image': f'{os.environ.get("AWS_CLOUD_FRONT_URL")}/{filename}'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=HTTP_RESPONSE_CODE_BAD_REQUEST)
    
    return JsonResponse({'error': 'Method Not Allowed'}, status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)
