import boto3, os

def subject_template(text):
  if text != '':
    return f'電波祭実行委員会'
  return f'{text}【電波祭実行委員会】'

def body_template(user, organization, text):
  return f'''
{user.username} ({organization.name}) 様

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

def send_mail(to, subject, message):
  
  if os.environ.get('DEBUG') == 'True':
    return
  
  AWS_SQS_URL = os.environ.get('AWS_MAIL_SQS_URL')
  client = boto3.client('sqs')
  
  try:
    response = client.send_message(
      QueueUrl = AWS_SQS_URL,
      MessageBody = f'{to},{subject_template(subject)},{body_template(message)}'
    )
    return response
  
  except Exception as e:
    return e
