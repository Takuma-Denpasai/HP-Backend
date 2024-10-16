from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from .constant import *
from .permission import *

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inspection(request, id):
  
  if checkPermission(request.user, id, [PERMISSION_ADMIN, PERMISSION_INSPECTION]):
    
    if request.method == 'GET':
      
      news = list(NewsInspectionData.objects.filter(ai=True, inspected=False, deleted=False).values('news__title', 'news__detail', 'news__user__username', 'news__organization__name', 'news__id', 'news__updated_at'))
      organization_permission = list(OrganizationPermissionInspectionData.objects.filter(inspected=False, deleted=False).values('organization__permission_type', 'organization__organization__name', 'organization__id', 'organization__updated_at'))
      post = list(PostInspectionData.objects.filter(ai=True, inspected=False, deleted=False).values('post__title', 'post__detail', 'post__user__username', 'post__organization__name', 'post__id', 'post__updated_at'))
      shop = list(ShopInspectionData.objects.filter(ai=True, inspected=False, deleted=False).values('shop__name', 'shop__detail', 'shop__user__username', 'shop__organization__name', 'shop__id', 'shop__updated_at'))
      menu = list(MenuInspectionData.objects.filter(ai=True, inspected=False, deleted=False).values('menu__name', 'menu__shop__name', 'menu__id', 'menu__updated_at'))
      event = list(EventInspectionData.objects.filter(ai=True, inspected=False, deleted=False).values('event__title', 'event__detail', 'event__user__username', 'event__organization__name', 'event__id', 'event__updated_at'))
      karaoke = list(KaraokeInspectionData.objects.filter(ai=True, inspected=False, deleted=False).values('karaoke__name', 'karaoke__user__username', 'karaoke__organization__name', 'karaoke__id', 'karaoke__updated_at'))
      band = list(BandInspectionData.objects.filter(ai=True, inspected=False, deleted=False).values('band__name', 'band__user__username', 'band__organization__name', 'band__id', 'band__updated_at'))
      band_song = list(BandSongInspectionData.objects.filter(ai=True, inspected=False, deleted=False).values('song__name', 'song__band__name', 'song__id'))
      
      return JsonResponse({'news': news, 'organization_permission': organization_permission, 'post': post, 'shop': shop, 'menu': menu, 'event': event, 'karaoke': karaoke, 'band': band, 'band_song': band_song})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def inspect(request, id, category, item_id):
  
  if checkPermission(request.user, id, [PERMISSION_ADMIN, PERMISSION_INSPECTION]):
    
    if request.method == 'GET':
      
      if not category in ['news', 'organization_permission', 'post', 'shop', 'menu', 'event', 'karaoke', 'band', 'band_song']:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      news = list(NewsInspectionData.objects.filter(news__id=item_id, ai=True, inspected=False, deleted=False).values('news__title', 'news__detail', 'news__user__username', 'news__organization__name', 'news__id', 'news__updated_at')) if category == 'news' else []
      organization_permission = list(OrganizationPermissionInspectionData.objects.filter(organization__id=item_id, inspected=False, deleted=False).values('organization__permission_type', 'organization__organization__name', 'organization__id', 'organization__updated_at')) if category == 'organization_permission' else []
      post = list(PostInspectionData.objects.filter(post__id=item_id, ai=True, inspected=False, deleted=False).values('post__title', 'post__detail', 'post__user__username', 'post__organization__name', 'post__id', 'post__updated_at')) if category == 'post' else []
      shop = list(ShopInspectionData.objects.filter(shop__id=item_id, ai=True, inspected=False, deleted=False).values('shop__name', 'shop__detail', 'shop__user__username', 'shop__organization__name', 'shop__id', 'shop__updated_at')) if category == 'shop' else []
      menu = list(MenuInspectionData.objects.filter(menu__id=item_id, ai=True, inspected=False, deleted=False).values('menu__name', 'menu__shop__name', 'menu__id', 'menu__updated_at')) if category == 'menu' else []
      event = list(EventInspectionData.objects.filter(event__id=item_id, ai=True, inspected=False, deleted=False).values('event__title', 'event__detail', 'event__user__username', 'event__organization__name', 'event__id', 'event__updated_at')) if category == 'event' else []
      karaoke = list(KaraokeInspectionData.objects.filter(karaoke__id=item_id, ai=True, inspected=False, deleted=False).values('karaoke__name', 'karaoke__user__username', 'karaoke__organization__name', 'karaoke__id', 'karaoke__updated_at')) if category == 'karaoke' else []
      band = list(BandInspectionData.objects.filter(band__id=item_id, ai=True, inspected=False, deleted=False).values('band__name', 'band__user__username', 'band__organization__name', 'band__id', 'band__updated_at')) if category == 'band' else []
      band_song = list(BandSongInspectionData.objects.filter(song__id=item_id, ai=True, inspected=False, deleted=False).values('song__name', 'song__band__name', 'song__id')) if category == 'band_song' else []
      
      count = len(news) + len(organization_permission) + len(post) + len(shop) + len(menu) + len(event) + len(karaoke) + len(band) + len(band_song)
      
      return JsonResponse({'count': count, 'news': news, 'organization_permission': organization_permission, 'post': post, 'shop': shop, 'menu': menu, 'event': event, 'karaoke': karaoke, 'band': band, 'band_song': band_song})
    
    elif request.method == 'POST':
      
      inspect_result = request.POST['approve'] == 'true'
      
      if category == 'news':
        
        news = NewsInspectionData.objects.filter(news__id=item_id, ai=True, inspected=False, deleted=False)
        
        if news.exists():
          
          news.update(inspected=inspect_result, user=request.user, deleted=not inspect_result, ai=False)
          return JsonResponse({'message': 'ニュースが検査されました。'})
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      elif category == 'organization_permission':
        
        organization_permission = OrganizationPermissionInspectionData.objects.filter(organization__id=item_id, ai=True, inspected=False, deleted=False)
        
        if organization_permission.exists():
          
          organization_permission.update(inspected=inspect_result, user=request.user, deleted=not inspect_result, ai=False)
          return JsonResponse({'message': '組織権限が検査されました。'})
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      elif category == 'post':
        
        post = PostInspectionData.objects.filter(post__id=item_id, ai=True, inspected=False, deleted=False)
        
        if post.exists():
          
          post.update(inspected=inspect_result, user=request.user, deleted=not inspect_result, ai=False)
          return JsonResponse({'message': '投稿が検査されました。'})
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      elif category == 'shop':
        
        shop = ShopInspectionData.objects.filter(shop__id=item_id, ai=True, inspected=False, deleted=False)
        
        if shop.exists():
          
          shop.update(inspected=inspect_result, user=request.user, deleted=not inspect_result, ai=False)
          return JsonResponse({'message': '店舗が検査されました。'})
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      elif category == 'menu':
        
        menu = MenuInspectionData.objects.filter(menu__id=item_id, ai=True, inspected=False, deleted=False)
        
        if menu.exists():
          
          menu.update(inspected=inspect_result, user=request.user, deleted=not inspect_result, ai=False)
          return JsonResponse({'message': 'メニューが検査されました。'})
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      elif category == 'event':
        
        event = EventInspectionData.objects.filter(event__id=item_id, ai=True, inspected=False, deleted=False)
        
        if event.exists():
          
          event.update(inspected=inspect_result, user=request.user, deleted=not inspect_result, ai=False)
          return JsonResponse({'message': 'イベントが検査されました。'})
        
        return