# geoip
GeoIP in python

This example MaxMind inserted into two DynamoDB tables:
- geoip_city_blocks_ip4_dev
- geoip_city_locations_dev

In order to deploy:

```
npm install -g serverless
npm install
sls deploy
```

API Gateway
![XRay Tracke](images/APIG.png)


Http Response in json
![XRay Tracke](images/Response.png)


XRay Traces
![XRay Tracke](images/XRayTrace.png)

![XRay Tracke](images/XRayMap.png)
