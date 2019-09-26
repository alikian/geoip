import boto3
from netaddr import *
import json
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()
dynamodb = boto3.resource('dynamodb')


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
