from .constant import *

def checkStatus(message):
  
  data = {}
  data['success'] = False
  data['message'] = message
  
  if message == STATUS_SUCCESS:
    
    data['success'] = True
  
  return data
