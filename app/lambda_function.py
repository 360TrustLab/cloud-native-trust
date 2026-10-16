import os,json,boto3
from botocore.exceptions import ClientError

def handler(event,context):
    if 'requestContext' in event:
        return {'statusCode':200,'body':json.dumps({'service':'360TrustLab','status':'ready','secret_values_displayed':False})}
    s3=boto3.client('s3');sm=boto3.client('secretsmanager');ddb=boto3.client('dynamodb')
    def read_doc(key):
        response=s3.get_object(Bucket=os.environ['BUCKET'],Key=key)
        response['Body'].close()
    cases=[
      ('Read intended document',lambda:read_doc('documents/example.txt')),
      ('Write application metadata',lambda:ddb.put_item(TableName=os.environ['TABLE'],Item={'id':{'S':'conference-probe'},'value':{'S':'synthetic'}})),
      ('Read integration secret',lambda:sm.get_secret_value(SecretId=os.environ['SECRET_ARN'])),
      ('Read unrelated document',lambda:read_doc('unrelated/example.txt')),
      ('Read unrelated secret',lambda:sm.get_secret_value(SecretId=os.environ['OTHER_SECRET_ARN'])),
    ]
    results=[]
    for name,operation in cases:
        try:
            operation();results.append({'name':name,'result':'ALLOW'})
        except ClientError as error:
            code=error.response['Error']['Code']
            if code not in ['AccessDenied','AccessDeniedException','UnauthorizedOperation']:
                results.append({'name':name,'result':'SETUP_ERROR','error_code':code})
            else:results.append({'name':name,'result':'DENY','error_code':code})
    return {'scope':'REAL AWS SDK request results inside Lambda','secret_values_displayed':False,'checks':results}
