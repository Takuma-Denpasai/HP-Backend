from .constant import *

def checkPermission(request_user, organization_id, permission_type):
  
  for permission in permission_type:
    
    if permission == PERMISSION_ADMIN:
      
      if request_user.permissions.filter(permission_type=permission).exists():
        
        return True
    
    elif permission == PERMISSION_INVITE_USER:
      
      if request_user.permissions.filter(permission_type=permission, organization_id=organization_id).exists():
        
        return True
    
    else:
      
      if request_user.permissions.filter(permission_type=permission, organization_id=organization_id).exists() and request_user.organization.filter(id=organization_id, organization_permissions__permission_type=permission).exists():
        
        return True
  
  return False
