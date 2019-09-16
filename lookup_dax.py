from netaddr import *
import json
import amazondax
import botocore.session
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

session = botocore.session.get_session()
endpoint = 'test2.ulsqhu.clustercfg.dax.usw2.cache.amazonaws.com:8111'
dynamodb = amazondax.AmazonDaxClient(session, region_name='us-west-2', endpoints=[endpoint])
print('Success')


def find(event, context):
    print('event')

    if event['pathParameters']:
        ip = event['pathParameters'].get('ip')
    else:
        ip = event['requestContext']['identity']['sourceIp']

    ip_response = find_subnets(ip, 'geoip_city_blocks_ip4_dev')[0]

    geoname_id = ip_response['geoname_id']
    geoname = find_geoname(geoname_id, 'geoip_city_locations_dev')
    ip_response['geoname'] = geoname

    response = {
        "statusCode": 200,
        "body": json.dumps(ip_response,
                           cls=DecimalEncoder)
    }
    return response


def find_subnets(ip, table):
    ipn = IPNetwork(ip)
    supernets = ipn.supernet(18)
    keys = []
    for supernet in reversed(supernets):
        keys.append({
            'network': {
                'S': str(supernet.cidr)
            }
        })
    networks = {
        table:
            {
                'Keys': keys
            }
    }
    print(networks)
    response = dynamodb.batch_get_item(RequestItems=networks)
    return response['Responses'][table]


def find_geoname(geoname_id, table):

    result = dynamodb.get_item(
        Key={
            'geoname_id':  geoname_id
        },
        TableName=table
    )
    return result['Item']


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)
