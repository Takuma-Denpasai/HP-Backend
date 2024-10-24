from datetime import datetime, timezone, timedelta
import os, random, string
JST = timezone(timedelta(hours=+9), 'JST')

PERMISSION_ADMIN = 'admin'
PERMISSION_SHOP = 'shop'
PERMISSION_NEWS = 'news'
PERMISSION_MENU = 'menu'
PERMISSION_EVENT = 'event'
PERMISSION_BAND = 'band'
PERMISSION_KARAOKE = 'karaoke'
PERMISSION_INVITE_USER = 'invite_user'
PERMISSION_INSPECTION = 'inspection'

HTTP_RESPONSE_CODE_SUCCESS = 200
HTTP_RESPONSE_CODE_CREATED = 201
HTTP_RESPONSE_CODE_BAD_REQUEST = 400
HTTP_RESPONSE_CODE_UNAUTHORIZED = 401
HTTP_RESPONSE_CODE_FORBIDDEN = 403
HTTP_RESPONSE_CODE_NOT_FOUND = 404
HTTP_RESPONSE_CODE_METHOD_NOT_ALLOWED = 405

def INSPECTION_APPROVE_MAIL(data_type, detail):
  
  if data_type == 'organization':
    url = f'{os.environ.get('FRONTEND_HOSTS')}/organization/{detail}/permission'
  else:
    url = f'{os.environ.get('FRONTEND_HOSTS')}/organization?next=/{data_type}/{detail}'
  
  return f'''
ユーザーから送信された内容が検証にて承認されましたことをご連絡いたします。

■検証日時
　{datetime.now(JST).strftime('%Y/%m/%d %H:%M:%S')}

■データタイプ
　{data_type}

■データID
　{detail}

{url}
'''

def INSPECTION_REJECT_MAIL(data_type, detail):
  
  if data_type == 'organization':
    url = f'{os.environ.get('FRONTEND_HOSTS')}/organization/{detail}/permission'
  else:
    url = f'{os.environ.get('FRONTEND_HOSTS')}/organization?next=/{data_type}/{detail}'
  
  return f'''
ユーザーから送信された内容が検証にて承認されましたことをご連絡いたします。

■検証日時
　{datetime.now(JST).strftime('%Y/%m/%d %H:%M:%S')}

■データタイプ
　{data_type}

■データID
　{detail}

{url}
'''

def randomString(n = 30):
  return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(n)])
