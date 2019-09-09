import boto3
from netaddr import *
import json

dynamodb = boto3.resource('dynamodb')


def find(event, context):
    print(event)
    if event['pathParameters']:
        ip = event['pathParameters'].get('ip')
    else:
        ip = event['requestContext']['identity']['sourceIp']

    ip_response = find_subnets(ip, 'geoip_city_blocks_ip4_dev')[0]

    geoname_id = ip_response['geoname_id']
    print(geoname_id)
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
            'network': str(supernet.cidr)
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
    geoname_table = dynamodb.Table(table)

    result = geoname_table.get_item(
        Key={
            'geoname_id': geoname_id
        }
    )
    return result['Item']


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)
