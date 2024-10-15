import boto3, os

def inspection(type, id):
  
  # if os.environ.get('DEBUG') == 'True':
    # return
  
  SQS_URL = os.environ.get('SQS_URL')
  client = boto3.client('sqs')
  
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
    print(e)
    return e
