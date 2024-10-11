from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from .constant import *

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_auth(request):
  
  return JsonResponse({'is_auth': request.user.is_authenticated, 'username': request.user.username})

# GET /news
def allNews(request):
  
  if request.method == 'GET':
    
    if 'top' in request.GET:
      
      news = list(NewsData.objects.filter(news_inspections__inspected=True, news_inspections__deleted=False, show_top=True).order_by('-created_at').values('id', 'title', 'organization__name', 'created_at'))
    
    elif 'important' in request.GET:
      
      news = list(NewsData.objects.filter(news_inspections__inspected=True, news_inspections__deleted=False, important=True).order_by('-created_at').values('id', 'title'))
    
    else:
      
      news = list(NewsData.objects.filter(news_inspections__inspected=True, news_inspections__deleted=False).order_by('-created_at').values('id', 'title', 'detail', 'show_top', 'important', 'organization__name', 'user__username', 'created_at', 'updated_at'))
    
    return JsonResponse({'news': news})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# GET/PUT /news/[id]
@api_view(['GET'])
def oneNews(request, id):
  
  if request.method == 'GET':
    
    news = list(NewsData.objects.filter(news_inspections__inspected=True, news_inspections__deleted=False, id=id).values('id', 'title', 'detail', 'show_top', 'important', 'organization__name', 'user__username', 'created_at', 'updated_at'))
    
    if len(news) == 0:
      return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    return JsonResponse({'news': news})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# ! 未対応
# POST /news/new
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def newNews(request, id):
  
  if request.method == 'POST':
    
    print(request.user.permissions__permission_type())
    
    news = NewsData.objects.create(
      title=request.POST.get('title'),
      detail=request.POST.get('detail'),
      show_top=request.POST.get('show_top'),
      important=request.POST.get('important'),
      organization_id=request.POST.get('organization_id'),
      user_id=request.user.id
    )
    
    inspection = NewsInspectionData.objects.create(news_id=news.id)
    
    return JsonResponse({'news': news})
