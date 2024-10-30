from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from .constant import *
from .permission import *
from .inspection import *
import json

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_auth(request):
  
  return JsonResponse({'is_auth': request.user.is_authenticated, 'username': request.user.username})

# GET /news
def allNews(request):
  
  if request.method == 'GET':
    
    if 'top' in request.GET:
      
      news = list(NewsData.objects.filter(news_inspections__inspected=True, news_inspections__deleted=False, show_top=True).order_by('-created_at').values('id', 'title', 'organization__name', 'user__username', 'created_at'))
    
    elif 'important' in request.GET:
      
      news = list(NewsData.objects.filter(news_inspections__inspected=True, news_inspections__deleted=False, important=True).order_by('-created_at').values('id', 'title', 'organization__name', 'user__username'))
    
    else:
      
      news = list(NewsData.objects.filter(news_inspections__inspected=True, news_inspections__deleted=False).order_by('-created_at').values('id', 'title', 'detail', 'show_top', 'important', 'organization__name', 'user__username', 'created_at', 'updated_at'))
    
    return JsonResponse({'news': news})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# GET/PUT /news/[id]
@api_view(['GET'])
def oneNews(request, id):
  
  if request.method == 'GET':
    
    news = list(NewsData.objects.filter(news_inspections__inspected=True, news_inspections__deleted=False, id=id).values('id', 'title', 'detail', 'show_top', 'important', 'organization__name', 'user__username', 'created_at', 'updated_at'))
    image = list(NewsImageData.objects.filter(news__id=id).values_list('image__image', flat=True))
    
    if len(news) == 0:
      return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    return JsonResponse({'news': news, 'image': image})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# GET /organization/[id]/news
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organizationNews(request, id):
  
  if request.method == 'GET':
    
    if checkPermission(request.user, id, [PERMISSION_NEWS]):
      
      organization = request.user.organization.filter(id=id)
      
      news = list(NewsData.objects.filter(organization=organization.first()).order_by('-updated_at').values('id', 'title', 'user__username', 'news_inspections__ai', 'news_inspections__inspected', 'news_inspections__deleted', 'created_at', 'updated_at'))
    
    return JsonResponse({'news': news})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# POST /organization/[id]/news/new
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def newNews(request, id):
  
  if request.method == 'POST':
    
    data = json.loads(request.body)
    image_urls = data.get('imageUrls', [])
    
    if checkPermission(request.user, id, [PERMISSION_NEWS]):
      
      if 'title' in data and 'detail' in data and 'show_top' in data and 'important' in data:
        
        organization = request.user.organization.filter(id=id)
        
        news = NewsData.objects.create(title=data['title'], detail=data['detail'], show_top=data['show_top'], important=data['important'], organization=organization.first(), user=request.user)
        
        NewsInspectionData.objects.create(news=news)
        
        add_photo = False
        for image in list(image_urls):
          if image != '':
            if NewsImageData.objects.filter(news=news, image__image=image).exists() == False:
              add_photo = True
              image_data = ImageData.objects.filter(image=image)
              NewsImageData.objects.create(news=news, image=image_data.first())
        
        if add_photo:
          inspection('news', news.id, False)
        else:
          inspection('news', news.id)
        
        return JsonResponse({'news': 'news'})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_BAD_REQUEST)

# GET/POST /organization/[id]/news/[id]
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def oneOrganizationNews(request, id, news_id):
  
  if request.method == 'GET':
    
    if checkPermission(request.user, id, [PERMISSION_NEWS]):
      
      organization = request.user.organization.filter(id=id)
      
      news = list(NewsData.objects.filter(organization=organization.first(), id=news_id).values('id', 'title', 'detail', 'show_top', 'important', 'organization__name', 'user__username', 'created_at', 'updated_at'))
      image = list(NewsImageData.objects.filter(news__id=news_id).values_list('image__image', flat=True))
      
      if len(news) == 0:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      return JsonResponse({'news': news, 'image': image})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
  
  elif request.method == 'POST':
    
    data = json.loads(request.body)
    print(data)
    
    if checkPermission(request.user, id, [PERMISSION_NEWS]):
      
      organization = request.user.organization.filter(id=id)
      image_urls = data.get('imageUrls', [])
      
      news = NewsData.objects.filter(organization=organization.first(), id=news_id)
      
      if news.exists() == False:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      else:
        news = news.first()
        
        if 'title' in data:
          news.title=data['title']
        
        if 'detail' in data:
          news.detail=data['detail']
        
        if 'show_top' in data:
          news.show_top=data['show_top']
        
        if 'important' in data:
          news.important=data['important']
        
        news.save()
        
        now_approve = NewsInspectionData.objects.filter(news=news).first().inspected
        NewsInspectionData.objects.filter(news=news).update(inspected=False, deleted=False, ai=False)
        
        add_photo = False
        before_images = list(NewsImageData.objects.filter(news=news).values_list('image__image', flat=True))
        for image in list(image_urls):
          if image != '':
            if image in before_images:
              before_images.remove(image)
            if NewsImageData.objects.filter(news=news, image__image=image).exists() == False:
              add_photo = True
              image_data = ImageData.objects.filter(image=image)
              NewsImageData.objects.create(news=news, image=image_data.first())
        
        for before_image in before_images:
          NewsImageData.objects.filter(news=news, image__image=before_image).delete()
        
        if add_photo or not now_approve:
          inspection('news', news_id, False)
        else:
          inspection('news', news_id)
      
      return JsonResponse({'news': 'success'})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)

# POST /organization/[id]/news/[id]/delete
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deleteOrganizationNews(request, id, news_id):
  
  if request.method == 'POST':
    
    if checkPermission(request.user, id, [PERMISSION_NEWS]):
      
      organization = request.user.organization.filter(id=id)
      
      news = NewsData.objects.filter(organization=organization.first(), id=news_id)
      
      if news.exists() == False:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      else:
        news = news.first()
        
        news.delete()
      
      return JsonResponse({'news': 'success'})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
