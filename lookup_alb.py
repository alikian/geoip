import boto3
from netaddr import *
import json
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import geoip

patch_all()
dynamodb = boto3.resource('dynamodb')


def find(event, context):
    print(event)
    path = event['path']
    ip = path[4:]
    print(ip)

    ip_response = geoip.find_subnets(ip, 'geoip_city_blocks_ip4_dev')[0]

    geoname_id = ip_response['geoname_id']
    geoname = geoip.find_geoname(geoname_id, 'geoip_city_locations_dev')
    ip_response['geoname'] = geoname

    response = {
        "statusCode": 200,
        "body": json.dumps(ip_response,
                           cls=geoip.DecimalEncoder),
        "headers": {
            "Content-Type": "application/json"
        },
    }
    return response
