import boto3, os
from .constant import *

def subject_template(text):
  if text == '':
    return f'電波祭実行委員会'
  return f'{text}【電波祭実行委員会】'

def body_template(user, text):
  return f'''
{user.username} 様

{text}

※このメールはシステムからの自動送信です。返信はお受けできませんのでご注意ください。

---------------------------------
電波祭実行委員会
香川高等専門学校 詫間キャンパス
〒769-1192 香川県三豊市詫間町香田551
takumadenpasai@gmail.com
https://denpafest.com
---------------------------------
'''

def send_mail(request, subject, message):
  
  if os.environ.get('DEBUG') == 'True':
    return
  
  print(request)
  
  AWS_SQS_URL = os.environ.get('AWS_MAIL_SQS_URL')
  client = boto3.client('sqs',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
                       )
  
  try:
    response = client.send_message(
      QueueUrl = AWS_SQS_URL,
      MessageBody = f'{request.email},{subject_template(subject)},{body_template(request, message)}',
      MessageGroupId='default',
      MessageDeduplicationId=randomString(30)
    )
    return response
  
  except Exception as e:
    print(e)
    return e
