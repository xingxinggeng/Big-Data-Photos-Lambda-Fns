import json
import boto3
import logging
from botocore.vendored import requests
#from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    print("Hello!!!!!!!!!!!!!!!!!!!")
    print("event: ", event)
    print("context: ", context)

    q = event["queryStringParameters"]["q"]
    print("q: ", q)
    
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName='photobot',
        botAlias='photobot',
        userId="lexbot",
        inputText=q
    )
    # res is non-deterministic
    # weird res
    print("lex res: ", response['slots'])
    
    keywords = []
    if response['slots']['keyOne'] is not None:
        keywords.append(response['slots']['keyOne'])
    if response['slots']['keyTwo'] is not None:
        keywords.append(response['slots']['keyTwo'])
    
    # search in opensearch
    host = "https://search-photos-jrtcl5jlxxsynomf5kuwqpixsq.us-east-1.es.amazonaws.com"
    auth = ('master', 'Cc_123456')
    search_results = []
    for keyword in keywords:
        #url = host+"/photos/_search?q="+"cat"
        if keyword.endswith('s'):
            end = len(keyword)-1
            keyword = keyword[:end]
        print("keyword: ", keyword)
        url = host+"/photos/_search?q="+keyword
        response = requests.get(url, auth=auth)
        response = response.json()
        
        for hit in response['hits']['hits']:
            result = {"key": hit['_source']['objectKey'], "labels": hit['_source']['labels']}
            search_results.append(result)
    print("search results: ", search_results)
            
    
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(search_results)
    }
