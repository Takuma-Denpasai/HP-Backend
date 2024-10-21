from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from .constant import *
from .permission import *
from .inspection import *
import datetime

# Create your views here.

# GET /shop
def allShop(request):
  
  if request.method == 'GET':
    
    if 'top' in request.GET:
      
      shop = list(ShopData.objects.filter(shop_inspection__inspected=True, shop_inspection__deleted=False).order_by('start').values('id', 'title', 'place', 'start', 'end', 'organization__name', 'user__username'))
    
    else:
      
      shop = list(ShopData.objects.filter(shop_inspection__inspected=True, shop_inspection__deleted=False).order_by('start').values('id', 'title', 'place', 'start', 'end', 'organization__name', 'user__username'))
    
    return JsonResponse({'shop': shop})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# GET /shop/[id]
@api_view(['GET'])
def oneShop(request, id):
  
  now = datetime.datetime.now(JST)
  
  if request.method == 'GET':
    
    shop = list(ShopData.objects.filter(shop_inspection__inspected=True, shop_inspection__deleted=False, id=id).values('id', 'title', 'place', 'detail', 'start', 'end', 'organization__name', 'user__username'))
    
    if len(shop) == 0:
      return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    return JsonResponse({'shop': shop})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# GET /organization/[id]/shop
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organizationShop(request, id):
  
  if request.method == 'GET':
    
    if checkPermission(request.user, id, [PERMISSION_SHOP]):
      
      organization = request.user.organization.filter(id=id)
      
      shop = list(ShopData.objects.filter(organization=organization.first()).order_by('-updated_at').values('id', 'title', 'user__username', 'shop_inspection__ai', 'shop_inspection__inspected', 'shop_inspection__deleted', 'created_at', 'updated_at'))
    
    return JsonResponse({'shop': shop})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# POST /organization/[id]/shop/new
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def newShop(request, id):
  
  if request.method == 'POST':
    
    data = request.POST
    
    if checkPermission(request.user, id, [PERMISSION_SHOP]):
      
      if 'title' in data and 'detail' in data and 'place' in data and 'start' in data and 'end' in data:
        
        organization = request.user.organization.filter(id=id)
        
        shop = ShopData.objects.create(organization=organization.first(), user=request.user, title=data['title'], detail=data['detail'], place=data['place'], start=datetime.datetime.strptime(data['start'] + ':00', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=JST), end=datetime.datetime.strptime(data['end'] + ':00', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=JST))
        
        ShopInspectionData.objects.create(shop=shop)
        
        inspection('shop', shop.id)
        
        return JsonResponse({'shop': 'shop'})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_BAD_REQUEST)

# GET/POST /organization/[id]/shop/[id]
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def oneOrganizationShop(request, id, shop_id):
  
  if request.method == 'GET':
    
    if checkPermission(request.user, id, [PERMISSION_SHOP]):
      
      organization = request.user.organization.filter(id=id)
      
      shop = list(ShopData.objects.filter(organization=organization.first(), id=shop_id).values('id', 'title', 'place', 'detail', 'start', 'end', 'organization__name', 'user__username', 'created_at', 'updated_at'))
      
      if len(shop) == 0:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      return JsonResponse({'shop': shop})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
  
  elif request.method == 'POST':
    
    data = request.POST
    
    if checkPermission(request.user, id, [PERMISSION_SHOP]):
      
      organization = request.user.organization.filter(id=id)
      
      shop = ShopData.objects.filter(organization=organization.first(), id=shop_id)
      
      if shop.exists() == False:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      else:
        shop = shop.first()
        
        shop.title=data['title']
        shop.detail=data['detail']
        shop.place=data['place']
        shop.start=datetime.datetime.strptime(data['start'] + ':00', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=JST)
        shop.end=datetime.datetime.strptime(data['end'] + ':00', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=JST)
        
        if shop.start > shop.end:
          return HttpResponse(status=HTTP_RESPONSE_CODE_BAD_REQUEST)
        else:
          shop.save()
        
        ShopInspectionData.objects.filter(shop=shop).update(inspected=False, deleted=False, ai=False)
        
        inspection('shop', shop_id)
      
      return JsonResponse({'shop': 'success'})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)

# POST /organization/[id]/shop/[id]/delete
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deleteOrganizationShop(request, id, shop_id):
  
  if request.method == 'POST':
    
    if checkPermission(request.user, id, [PERMISSION_SHOP]):
      
      organization = request.user.organization.filter(id=id)
      
      shop = ShopData.objects.filter(organization=organization.first(), id=shop_id)
      
      if shop.exists() == False:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      else:
        shop = shop.first()
        
        shop.delete()
      
      return JsonResponse({'shop': 'success'})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
