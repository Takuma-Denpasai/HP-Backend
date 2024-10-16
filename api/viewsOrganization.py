from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permission import checkPermission
from .constant import *
from .status import *
from .models import *

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrganization(request):
  
  if request.method == 'GET':
    
    organizations = list(request.user.organization.all().values('id', 'name', 'owner__username'))
    
    if len(organizations) == 0:
      
      return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    
    return JsonResponse({'organizations': organizations})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOneOrganization(request, id):
  
  if request.method == 'GET':
    
    organizations = list(request.user.organization.filter(id=id).values('id', 'name', 'owner__username'))
    
    permissions = list(request.user.permissions.filter(organization_id=id).values_list('permission_type', flat=True))
    
    delete = request.user.organization.filter(id=id).first().owner == request.user
    
    if len(organizations) == 0:
      
      if OrganizationData.objects.filter(id=id).exists():
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
      
      else:
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    
    return JsonResponse({'organizations': organizations, 'permissions': permissions, 'delete': delete})
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def newOrganization(request):
  
  if request.method == 'POST':
    
    if not 'name' in request.POST:
      
      return HttpResponse(status=HTTP_RESPONSE_CODE_BAD_REQUEST)
    
    organization = OrganizationData.objects.create(
      name=request.POST['name'],
      owner=request.user
    )
    
    PermissionData.objects.create(
      permission_type='invite_user',
      organization=organization,
      user=request.user
    )
    
    request.user.organization.add(organization)
    
    return JsonResponse({'organization': list(organization.values('name', 'owner'))}, status=HTTP_RESPONSE_CODE_CREATED)
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrganizationUsers(request, id):
  
  if request.method == 'GET':
    
    if request.user.organization.filter(id=id).exists():
      
      organization = request.user.organization.filter(id=id)
      
      organization_list = list(organization.values('id', 'name', 'owner_id'))
      
      users = organization.first().users.all()
      user_list = []
      
      for user in users:
          permissions = list(user.permissions.filter(organization=organization.first()).values_list('permission_type', flat=True))
          user_list.append({
              'id': user.id,
              'username': user.username,
              'permissions': permissions
          })
      
      add = request.user.permissions.filter(Q(organization=organization.first()), Q(permission_type='admin') | Q(permission_type='invite_user')).exists()
      
      return JsonResponse({'organizations': organization_list, 'users': user_list, 'add': add })
    
    else:
      
      if OrganizationData.objects.filter(id=id).exists():
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
      
      else:
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def getOrganizationUsersPermission(request, id, user_id):
  
  add = checkPermission(request.user, id, ['admin', 'invite_user'])
  
  if request.method == 'GET':
    
    organization = request.user.organization.filter(id=id)
    
    organization_permissions = list(organization.first().organization_permissions.filter(organization_permission_inspection__inspected=True).values_list('permission_type', flat=True))
    
    if organization.exists():
      
      user = organization.first().users.filter(id=user_id)
      
      users = list(user.values('id', 'username'))
      
      if user.exists():
        
        permissions = list(user.first().permissions.filter(organization=organization.first()).values_list('permission_type', flat=True))
    
    else:
        
        if OrganizationData.objects.filter(id=id).exists():
          
          return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
        
        else:
          
          return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    
    return JsonResponse({
      'users': users, 
      'permissions': permissions, 
      'organization_permissions': organization_permissions,
      'add': add, 
      'is_owner': organization.first().owner_id == user.first().id, 
      'owner': organization.first().owner_id == request.user.id,
      })
  
  elif request.method == 'POST':
    
    if checkPermission(request.user, id, ['admin', 'invite_user']):
      
      organization = request.user.organization.filter(id=id)
      
      if organization.exists():
        
        user = organization.first().users.filter(id=user_id)
        
        if user.exists():
          
          after_permission = request.POST['permissions'].split(',')
          
          before_permission = user.first().permissions.filter(organization=organization.first())
          before_permission_list = list(before_permission.values_list('permission_type', flat=True))
          
          for permission in before_permission:
            if permission.permission_type not in after_permission:
              permission.delete()
          
          for permission in after_permission:
            if permission not in before_permission_list:
              if permission != "":
                PermissionData.objects.create(
                  permission_type=permission,
                  organization=organization.first(),
                  user=user.first()
                )
          
          if organization.first().owner == user.first():
            
            if not user.first().permissions.filter(permission_type=PERMISSION_INVITE_USER, organization=organization.first()).exists():
              
              PermissionData.objects.create(
                user = user.first(),
                organization = organization,
                permission_type = PERMISSION_INVITE_USER 
              )
          
          return HttpResponse(status=HTTP_RESPONSE_CODE_CREATED)
        
        else:
          return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
      
      else:
          
          if OrganizationData.objects.filter(id=id).exists():
            
            return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
          
          else:
            
            return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    
    else:
      return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrganizationUser(request, id):
  
  if request.method == 'POST':
    
    organization = request.user.organization.filter(id=id)
    
    if checkPermission(request.user, id, ['admin', 'invite_user']) and organization.exists():
      
      new_user = request.POST['username']
      
      user = UserData.objects.filter(username=new_user)
      
      if user.exists():
        
        user.first().organization.add(organization.first())
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_CREATED)
      
      else:
        return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
    else:
      return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
  
  return HttpResponse(status=HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deleteOrganizationUser(request, id, user_id):
  
  organizations = request.user.organization.filter(id=id)
  
  if organizations.exists():
    
    user = organizations.first().users.filter(id=user_id)
    
    if user.exists():
      
      organization = organizations.first()
      
      PermissionData.objects.filter(user=user.first(), organization=organization).delete()
      
      user.first().organization.remove(organization)
      
      return HttpResponse(status=HTTP_RESPONSE_CODE_CREATED)
  
  if OrganizationData.objects.filter(id=id).exists():
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
  
  else:
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changeOwner(request, id, user_id):
  
  organizations = request.user.organization.filter(id=id)
  
  if organizations.exists() and organizations.first().owner == request.user:
    
    user = organizations.first().users.filter(id=user_id)
    
    if user.exists():
      
      organization = organizations.first()
      
      organization.owner = user.first()
      
      organization.save()
      
      if not user.first().permissions.filter(permission_type=PERMISSION_INVITE_USER, organization=organization).exists():
        
        PermissionData.objects.create(
          user = user.first(),
          organization = organization,
          permission_type = PERMISSION_INVITE_USER 
        )
      
      return HttpResponse(status=HTTP_RESPONSE_CODE_CREATED)
    
    else:
      
      return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
  
  if OrganizationData.objects.filter(id=id).exists():
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
  
  else:
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deleteOrganization(request, id):
  
  organizations = request.user.organization.filter(id=id)
  
  if organizations.exists() and organizations.first().owner == request.user:
    
    organization = organizations.first()
    
    organization.delete()
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_CREATED)
  
  if OrganizationData.objects.filter(id=id).exists():
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
  
  else:
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def organizationPermission(request, id):
  
  organization = request.user.organization.filter(id=id)
  
  organization_permissions = list(organization.first().organization_permissions.all().order_by('-created_at').values('id', 'permission_type', 'created_at', 'organization_permission_inspection__inspected', 'organization_permission_inspection__deleted'))
  
  if organization.exists():
    
    if request.method == "GET":
      
      permissions = list(organization.first().organization_permissions.all().values_list('permission_type', flat=True))
      
      return JsonResponse({'permissions': permissions, 'now_permissions': organization_permissions})
    
    elif request.method == "POST":
      
      permission = request.POST['permission']
      
      organization_permission = OrganizationPermissionData.objects.create(
        permission_type=permission,
        organization=organization.first()
      )
      
      OrganizationPermissionInspectionData.objects.create(
        organization=organization_permission
      )
      
      return JsonResponse({'permission': list(organization_permission.values('permission_type', 'organization'))}, status=HTTP_RESPONSE_CODE_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def editOrganization(request, id):
  
  organization = request.user.organization.filter(id=id)
  
  if organization.exists():
    
    if request.method == "GET":
      
        if organization.first().owner == request.user:
          
          return JsonResponse({'organization': list(organization.values('id', 'name', 'owner_id'))})
      
    elif request.method == "POST":
      
      if 'name' in request.POST:
        
        organization.update(name=request.POST['name'])
        
        return JsonResponse({'organization': 'success'}, status=HTTP_RESPONSE_CODE_CREATED)
      
      else:
        
        return HttpResponse(status=HTTP_RESPONSE_CODE_BAD_REQUEST)
  
  if OrganizationData.objects.filter(id=id).exists():
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_FORBIDDEN)
  
  else:
    
    return HttpResponse(status=HTTP_RESPONSE_CODE_NOT_FOUND)
