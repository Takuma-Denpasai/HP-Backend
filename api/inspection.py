import boto3, os

def inspection(type, id):
  
  SQS_URL = os.environ.get('SQS_URL')
  client = boto3.client(
    'sqs',
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name = os.environ.get('AWS_DEFAULT_REGION')
  )
  
  def formatDBName(type):
    return type.lower()
  
  try:
    
    response = client.send_message(
      QueueUrl = SQS_URL,
      MessageBody = formatDBName(type) + ',' + str(id)
    )
    print(response)
    return response
  
  except Exception as e:
    print('Inspection', e)
    return e
