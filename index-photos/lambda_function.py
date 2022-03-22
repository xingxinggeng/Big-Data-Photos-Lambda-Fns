import json
import urllib.parse
import boto3
import logging
from botocore.vendored import requests
#from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

print('Loading function')

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    # bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    # try:
    #     response = s3.get_object(Bucket=bucket, Key=key)
    #     print("CONTENT TYPE: " + response['ContentType'])
    #     return response['ContentType']
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    create_time = event['Records'][0]['eventTime']
    
    # Get labels from rekognition.detect_labels
    response = rekognition.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':key}}, MaxLabels=10, MinConfidence=75)
    
    labels = []
    for label in response['Labels']:
        labels.append(label['Name'])
    
    print("Reko labels: ", labels)
        
    # Get x-amz-meta-customLabels from s3.head_object
    response = s3.head_object(Bucket=bucket, Key=key)
    if 'x-amz-meta-customLabels' in response:
        print("customLabels: ", response['x-amz-meta-customLabels'])
        labels.extend(response['x-amz-meta-customLabels'])
    else:
        print("x-amz-meta-customLabels is not applicable!")
    
    
    # index and post to opensearch
    index = {"objectKey": key, "bucket": bucket, "createdTimestamp": create_time,"labels": labels}
    
    host = "https://search-photos-jrtcl5jlxxsynomf5kuwqpixsq.us-east-1.es.amazonaws.com"
    auth = ('master', 'Cc_123456')

    
    url = host+"/photos/_doc"
    response = requests.post(url, auth=auth, json=index)
    response = response.text
    print("response: ", response)
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
    
    
    
    
    
    
    
    