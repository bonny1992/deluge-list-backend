import os, time
from deluge_client import DelugeRPCClient, FailedToReconnectException
from bottle import Bottle, run, route, request, abort
from truckpad.bottle.cors import CorsPlugin, enable_cors

DELUGE_ADDR = os.getenv('DELUGE_ADDR', '127.0.0.1')
DELUGE_PORT = os.getenv('DELUGE_PORT', 58846)
DELUGE_USER = os.getenv('DELUGE_USER', 'deluge')
DELUGE_PASS = os.getenv('DELUGE_PASS', '')

print(DELUGE_ADDR, DELUGE_PORT, DELUGE_USER, DELUGE_PASS)

app = Bottle()

@app.route('/')
def index():
    return abort(404)

@enable_cors
@app.route('/torrents/list', method='POST')
def list_torrents():
    with DelugeRPCClient(DELUGE_ADDR, int(DELUGE_PORT), DELUGE_USER, DELUGE_PASS) as client:
        torrents = client.call('core.get_torrents_status', {}, ['name'])

    torrent_list = []
    for i,j in torrents.items():
        temp = {}
        temp['torrent_id'] = i.decode("utf-8")
        for x,y in j.items():
            temp['torrent_name'] = y.decode("utf-8")
        torrent_list.append(temp)
    if not request.json or not request.json['search_for']:
        return dict(torrents=torrent_list)
    search_for = request.json['search_for']
    result = []
    for torrent in torrent_list:
        if search_for in torrent['torrent_name'].lower():
            result.append(torrent)
    return dict(torrents=result)

@enable_cors
@app.route('/torrents/delete', method='POST')
def delete_torrent():
    if not request.json or not request.json['torrent_id']:
        return {
            'error': 'Request JSON not correct',
            'code': 10,
        }
    torrent_id = request.json['torrent_id']
    data = {
        'torrent_id' : torrent_id,
        'remove_data': True
    }
    with DelugeRPCClient(DELUGE_ADDR, int(DELUGE_PORT), DELUGE_USER, DELUGE_PASS) as client:
        # result = client.call('core.remove_torrent', data)    
        result = client.core.remove_torrent(torrent_id, True)
    if result:
        return {
            'torrent_id': torrent_id,
            'success': 'success',
            'code': 0,
        }
    else:
        return {
            'torrent_id': torrent_id,
            'error': 'Error deleting the torrent',
            'code': 11,
            'result': result
        }
            
app.install(CorsPlugin(origins=['*']))





if __name__ == '__main__':
    run(app, host='localhost', port=8080)