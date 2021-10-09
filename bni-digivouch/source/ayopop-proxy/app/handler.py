from aiohttp import web
import requests, os, logging, json, jwt

routes = web.RouteTableDef()
AYOPOP_URL = os.getenv('AYOPOP_URL', default="https://dev.openapi.ayopop.id/api/")
AYOPOP_KEY = os.getenv('AYOPOP_KEY', default="DKfMyNbLtjsP")
AYOPOP_SECRET = os.getenv('AYOPOP_SECRET', default="SaUbZVUWSjWPTn1VSyUQq69KU4h2d7NjJc1")

logging.basicConfig(level=logging.DEBUG)

@routes.get('/healthcheck')
async def handler_healthcheck(request):
    dummy_response = vars()
    return web.Response(text=str(dummy_response), content_type='application/json', status=200)


@routes.get('/{tail:.*}')
async def handler_get(request):
    uri_path = request.match_info['tail']
    r = requests.get(AYOPOP_URL + uri_path)
    return web.Response(text=r.text, content_type='application/json', status=r.status_code)

@routes.post('/{tail:.*}')
async def handler_post(request):
    uri_path = request.match_info['tail']
    if request.body_exists: 
        json_body = await request.json()
    else:
        json_body = None

    KEY = AYOPOP_KEY
    SECRET = AYOPOP_SECRET

    encoded_jwt = jwt.encode(json_body, SECRET, algorithm="HS256")
    
    headers = { 'KEY': KEY, 
        'TOKEN': encoded_jwt, 
        'VERSION': '1.0'}
    
    r = requests.post(AYOPOP_URL + uri_path, json=json_body, headers=headers)
    logging.info("headers: %s", str(headers))
    logging.info("json_body: %s", str(json_body))
    logging.info("response: %s", r.text)
    return web.Response(text=r.text, content_type='application/json', status=r.status_code)

@routes.put('/{tail:.*}')
async def handler_put(request):
    uri_path = request.match_info['tail']
    if request.body_exists: 
        json_body = await request.json()
    else:
        json_body = None
    r = requests.put(AYOPOP_URL + uri_path, json=json_body)
    return web.Response(text=r.text, content_type='application/json', status=r.status_code)

@routes.delete('/{tail:.*}')
async def handler_delete(request):
    uri_path = request.match_info['tail']
    if request.body_exists: 
        json_body = await request.json()
    else:
        json_body = None
    r = requests.delete(AYOPOP_URL + uri_path, json=json_body)
    return web.Response(text=r.text, content_type='application/json', status=r.status_code)
        
app = web.Application()
app.add_routes(routes)
web.run_app(app)