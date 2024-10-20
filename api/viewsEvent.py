from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from .constant import *
from .permission import *
from .inspection import *
import datetime, json

# Create your views here.
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

# GET /event
def allEvent(request):
  
  if request.method == 'GET':
    
    now = datetime.datetime.now(JST)
    
    if 'top' in request.GET:
      
      event = list(EventData.objects.filter(event_inspection__inspected=True, event_inspection__deleted=False).order_by('start').values('id', 'title', 'place', 'start', 'end', 'organization__name', 'user__username'))
    
    else:
      
      event = list(EventData.objects.filter(event_inspection__inspected=True, event_inspection__deleted=False).order_by('start').values('id', 'title', 'place', 'start', 'end', 'organization__name', 'user__username'))
    
    return JsonResponse({'event': event, 'now': now})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# GET /event/[id]
@api_view(['GET'])
def oneEvent(request, id):
  
  now = datetime.datetime.now(JST)
  
  if request.method == 'GET':
    
    event = list(EventData.objects.filter(event_inspection__inspected=True, event_inspection__deleted=False, id=id).values('id', 'title', 'place', 'detail', 'start', 'end', 'organization__name', 'user__username'))
    image = list(EventImageData.objects.filter(event__id=id).values_list('image__image', flat=True))
    
    if len(event) == 0:
      return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    return JsonResponse({'event': event, 'now': now, 'image': image})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# GET /organization/[id]/event
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organizationEvent(request, id):
  
  if request.method == 'GET':
    
    if checkPermission(request.user, id, [PERMISSION_EVENT]):
      
      organization = request.user.organization.filter(id=id)
      
      event = list(EventData.objects.filter(organization=organization.first()).order_by('-updated_at').values('id', 'title', 'user__username', 'event_inspection__ai', 'event_inspection__inspected', 'event_inspection__deleted', 'created_at', 'updated_at'))
    
    return JsonResponse({'event': event})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

# POST /organization/[id]/event/new
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def newEvent(request, id):
  
  if request.method == 'POST':
    
    data = json.loads(request.body)
    image_urls = data.get('imageUrls', [])
    print(data)
    
    if checkPermission(request.user, id, [PERMISSION_EVENT]):
      
      if 'title' in data and 'detail' in data and 'place' in data and 'start' in data and 'end' in data:
        
        organization = request.user.organization.filter(id=id)
        
        event = EventData.objects.create(organization=organization.first(), user=request.user, title=data['title'], detail=data['detail'], place=data['place'], start=datetime.datetime.strptime(data['start'] + ':00', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=JST), end=datetime.datetime.strptime(data['end'] + ':00', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=JST))
        
        EventInspectionData.objects.create(event=event)
        
        add_photo = False
        for image in image_urls:
          if image != '':
            if EventImageData.objects.filter(event=event, image__image=image).exists() == False:
              add_photo = True
              image_data = ImageData.objects.filter(image=image)
              EventImageData.objects.create(event=event, image=image_data.first())
        
        if add_photo:
          inspection('event', event.id, False)
        else:
          inspection('event', event.id)
        
        return JsonResponse({'event': 'event'})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_BAD_REQUEST)

# GET/POST /organization/[id]/event/[id]
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def oneOrganizationEvent(request, id, event_id):
  
  if request.method == 'GET':
    
    if checkPermission(request.user, id, [PERMISSION_EVENT]):
      
      organization = request.user.organization.filter(id=id)
      
      event = list(EventData.objects.filter(organization=organization.first(), id=event_id).values('id', 'title', 'place', 'detail', 'start', 'end', 'organization__name', 'user__username', 'created_at', 'updated_at'))
      image = list(EventImageData.objects.filter(event__id=event_id).values_list('image__image', flat=True))
      
      if len(event) == 0:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      return JsonResponse({'event': event, 'image': image})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
  
  elif request.method == 'POST':
    
    data = json.loads(request.body)
    image_urls = data.get('imageUrls', [])
    
    if checkPermission(request.user, id, [PERMISSION_EVENT]):
      
      organization = request.user.organization.filter(id=id)
      
      event = EventData.objects.filter(organization=organization.first(), id=event_id)
      
      if event.exists() == False:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      else:
        event = event.first()
        
        event.title=data['title']
        event.detail=data['detail']
        event.place=data['place']
        event.start=datetime.datetime.strptime(data['start'] + ':00', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=JST)
        event.end=datetime.datetime.strptime(data['end'] + ':00', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=JST)
        
        if event.start > event.end:
          return HttpResponse(status=HTTP_RESPONSE_CODE_BAD_REQUEST)
        else:
          event.save()
        
        now_approve = EventInspectionData.objects.filter(event=event).first().inspected
        EventInspectionData.objects.filter(event=event).update(inspected=False, deleted=False, ai=False)
        
        add_photo = False
        before_images = list(EventImageData.objects.filter(event=event).values_list('image__image', flat=True))
        for image in image_urls:
          if image != '':
            if image in before_images:
              before_images.remove(image)
            if EventImageData.objects.filter(event=event, image__image=image).exists() == False:
              add_photo = True
              image_data = ImageData.objects.filter(image=image)
              EventImageData.objects.create(event=event, image=image_data.first())
        
        for before_image in before_images:
          EventImageData.objects.filter(event=event, image__image=before_image).delete()
        
        if add_photo or not now_approve:
          inspection('event', event_id, False)
        else:
          inspection('event', event_id)
      
      return JsonResponse({'event': 'success'})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)

# POST /organization/[id]/event/[id]/delete
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deleteOrganizationEvent(request, id, event_id):
  
  if request.method == 'POST':
    
    if checkPermission(request.user, id, [PERMISSION_EVENT]):
      
      organization = request.user.organization.filter(id=id)
      
      event = EventData.objects.filter(organization=organization.first(), id=event_id)
      
      if event.exists() == False:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      else:
        event = event.first()
        
        event.delete()
      
      return JsonResponse({'event': 'success'})
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
