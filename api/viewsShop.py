from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from .constant import *
from .permission import *
from .inspection import *
import json

# Create your views here.

# GET /shop
def allShop(request):
  
  if request.method == 'GET':
    
    shop = list(ShopData.objects.filter(shop_inspection__inspected=True, shop_inspection__deleted=False).order_by('-updated_at').values('id', 'name', 'address', 'image__image__image', 'organization__name', 'user__username'))
    
    return JsonResponse({'shop': shop})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# GET /shop/[id]
@api_view(['GET'])
def oneShop(request, id):
  
  if request.method == 'GET':
    
    shop = list(ShopData.objects.filter(shop_inspection__inspected=True, shop_inspection__deleted=False, id=id).values('id', 'name', 'address', 'image__image__image', 'detail', 'organization__name', 'user__username'))
    menu = list(MenuData.objects.filter(menu_inspection__inspected=True, menu_inspection__deleted=False, shop__id=id).values('id', 'name', 'price'))
    image = list(ShopImageData.objects.filter(shop__id=id).values_list('image__image', flat=True))
    
    if len(shop) == 0:
      return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    return JsonResponse({'shop': shop, 'menu': menu, 'image': image})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# GET /organization/[id]/shop
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organizationShop(request, id):
  
  if request.method == 'GET':
    
    if checkPermission(request.user, id, [PERMISSION_SHOP]):
      
      organization = request.user.organization.filter(id=id)
      
      shop = list(ShopData.objects.filter(organization=organization.first()).order_by('-updated_at').values('id', 'name', 'address', 'user__username', 'shop_inspection__ai', 'shop_inspection__inspected', 'shop_inspection__deleted', 'created_at', 'updated_at'))
    
    return JsonResponse({'shop': shop})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# POST /organization/[id]/shop/new
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def newShop(request, id):
  
  if request.method == 'POST':
    
    data = json.loads(request.body)
    image_urls = data.get('imageUrls', [])
    menus = data.get('menus', [])
    
    if checkPermission(request.user, id, [PERMISSION_SHOP]):
      
      organization = request.user.organization.filter(id=id)
      
      shop = ShopData.objects.create(organization=organization.first(), user=request.user, name=data['name'], detail=data['detail'], address=data['address'])
      
      ShopInspectionData.objects.create(shop=shop)
      
      add_photo = False
      for image in image_urls:
        if image != '':
          if ShopImageData.objects.filter(shop=shop, image__image=image).exists() == False:
            add_photo = True
            image_data = ImageData.objects.filter(image=image)
            ShopImageData.objects.create(shop=shop, image=image_data.first())
      
      if len(image_urls) != 0:
        shop.image = ShopImageData.objects.filter(shop=shop, image__image=image_urls[0]).first()
        shop.save()
      
      for menu in menus:
        menu_obj = MenuData.objects.create(shop=shop, name=menu['name'], price=menu['price'], user=request.user)
        MenuInspectionData.objects.create(menu=menu_obj)
        inspection('menu', menu_obj.id)
      
      if add_photo:
        inspection('shop', shop.id, False)
      else:
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
      
      shop = list(ShopData.objects.filter(organization=organization.first(), id=shop_id).values('id', 'name', 'address', 'detail', 'organization__name', 'user__username', 'created_at', 'updated_at'))
      image = list(ShopImageData.objects.filter(shop__id=shop_id).values_list('image__image', flat=True))
      menu = list(MenuData.objects.filter(shop__id=shop_id).values('id', 'name', 'price'))
      
      if len(shop) == 0:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      return JsonResponse({'shop': shop, 'menu': menu, 'image': image})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
  
  elif request.method == 'POST':
    
    data = json.loads(request.body)
    image_urls = data.get('imageUrls', [])
    menus = data.get('menus', [])
    
    if checkPermission(request.user, id, [PERMISSION_SHOP]):
      
      organization = request.user.organization.filter(id=id)
      
      shop = ShopData.objects.filter(organization=organization.first(), id=shop_id)
      
      if shop.exists() == False:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      else:
        shop = shop.first()
        
        shop.name=data['name']
        shop.detail=data['detail']
        shop.address=data['address']
        
        shop.save()
        
        now_approve = ShopInspectionData.objects.filter(shop=shop).first().inspected
        ShopInspectionData.objects.filter(shop=shop).update(inspected=False, deleted=False, ai=False)
        
        add_photo = False
        before_images = list(ShopImageData.objects.filter(shop=shop).values_list('image__image', flat=True))
        for index, image in enumerate(image_urls):
          if image != '':
            if image in before_images:
              before_images.remove(image)
            if ShopImageData.objects.filter(shop=shop, image__image=image).exists() == False:
              add_photo = True
              image_data = ImageData.objects.filter(image=image)
              ShopImageData.objects.create(shop=shop, image=image_data.first())
            if index == 0:
              shop.image = ShopImageData.objects.filter(shop=shop, image__image=image).first()
              shop.save()
        
        del_menu = list(MenuData.objects.filter(shop=shop).values_list('id', flat=True))
        
        for menu in menus:
          if MenuData.objects.filter(shop=shop, id=menu['id']).exists():
            MenuData.objects.filter(shop=shop, id=menu['id']).update(name=menu['name'], price=menu['price'])
            menu_obj = MenuData.objects.filter(shop=shop, id=menu['id']).first()
            MenuInspectionData.objects.filter(menu=menu_obj).update(inspected=False, deleted=False, ai=False)
            if menu_obj.id in del_menu:
              del_menu.remove(menu_obj.id)
          else:
            menu_obj = MenuData.objects.create(shop=shop, name=menu['name'], price=menu['price'], user=request.user)
            MenuInspectionData.objects.create(menu=menu_obj)
          inspection('menu', menu_obj.id)
        
        for del_id in del_menu:
          MenuData.objects.filter(shop=shop, id=del_id).delete()
        
        for before_image in before_images:
          ShopImageData.objects.filter(shop=shop, image__image=before_image).delete()
        
        if add_photo or not now_approve:
          inspection('shop', shop_id, False)
        else:
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
