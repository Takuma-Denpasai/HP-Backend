import boto3, os

def send_mail(to, subject, message):
  
  if os.environ.get('DEBUG') == 'True':
    return
  
  AWS_SQS_URL = os.environ.get('AWS_MAIL_SQS_URL')
  client = boto3.client('sqs')
  
  try:
    response = client.send_message(
      QueueUrl = AWS_SQS_URL,
      MessageBody = f'{to},{subject},{message}'
    )
    return response
  
  except Exception as e:
    return e
