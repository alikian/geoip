from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')


def load_all(event, context):
    load('https://geolite.maxmind.com/download/geoip/database/GeoLite2-City-CSV.zip',
         'GeoLite2-City-CSV_20190903/GeoLite2-City-Locations-en.csv',
         'geoip_city_locations_dev')
    load('https://geolite.maxmind.com/download/geoip/database/GeoLite2-City-CSV.zip',
         'GeoLite2-City-CSV_20190903/GeoLite2-City-Blocks-IPv4.csv',
         'geoip_city_blocks_ip4_dev')


def load(url, file, table):
    resp = urlopen(url)
    zipfile = ZipFile(BytesIO(resp.read()))
    stream = zipfile.open(file)

    header_line = stream.readline().decode('utf-8')
    header_fields = header_line.split(',')

    records = []
    batch_size = 25
    records_count = 0
    for line in stream.readlines():
        fields = line.decode('utf-8').split(',')
        item = {}
        counter = 0
        for header_field in header_fields:
            value = fields[counter]
            if value:
                item[header_field] = fields[counter]
            counter += 1
        record = {
            'PutRequest': {
                'Item': item
            }
        }
        records.append(record)

        if len(records) == batch_size:
            records_count += len(records)
            print('Record inserted '+str(records_count))
            batch_write(table, records)
            records = []

    batch_write(table, records)


def batch_write(table, records):
    dynamodb.batch_write_item(RequestItems={
        table: records}
    )


load('https://geolite.maxmind.com/download/geoip/database/GeoLite2-City-CSV.zip',
     'GeoLite2-City-CSV_20190903/GeoLite2-City-Blocks-IPv4.csv',
     'geoip_city_blocks_ip4_dev')
