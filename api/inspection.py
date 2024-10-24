import boto3, os

def inspection(type, id, allow_approve = True):
  
  if os.environ.get('DEBUG') == 'True':
    return
  
  AWS_SQS_URL = os.environ.get('AWS_INSPECTION_SQS_URL')
  client = boto3.client('sqs')
  
  def formatDBName(type):
    return type.lower()
  
  try:
    response = client.send_message(
      QueueUrl = AWS_SQS_URL,
      MessageBody = formatDBName(type) + ',' + str(id) + ',' + str(allow_approve)
    )
    return response
  
  except Exception as e:
    print(e)
    return e
