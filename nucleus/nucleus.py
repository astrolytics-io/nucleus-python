import locale, socket, struct, getpass, platform
import time, datetime
import threading
import traceback
import random
import json

import websocket
import pickledb
import appdirs

from utils import get_total_ram, get_machine_id, merge_dicts, generate_user_id


# Options
api_url = "app.nucleus.sh"
report_interval = 20 # s between reportings
app_id = None
disable_tracking = False
user_id = None
dev = False
dev_mode = False
debug = False

# Cache
db = None
queue = None
props = None
ws = None

def log(message):
	if (debug):
		print('Nucleus: '+message)

def log_error(message):
	print('Nucleus error: '+message)


# User data
ram = get_total_ram()
arch = struct.calcsize("P") * 8
hostname = socket.gethostname()
username = getpass.getuser()
version = "0.0.0"

try:
	locale = locale.getdefaultlocale()[0]
except:
	log_error('Could not detect user language (probably the MacOS bug)')
	locale = None

machine_id = get_machine_id()
session_id = random.randint(1000, 9999)
os_name = platform.system()
os_version = platform.release()
module_version = "0.2"


def app_started():
	global db, queue, props

	if not app_id:
		log_error("set app_id before you can start tracking")

	db_path = appdirs.user_cache_dir()
	filename = 'nucleus-'+app_id

	# Restore DB
	db = pickledb.load(db_path + '/' +filename, True)
	queue = db.get('queue') or []
	props = db.get('props') or {}

	# Regularly run the function to let the server know client is still connected
	timer = threading.Timer(report_interval, report_data)
	timer.daemon = True
	timer.start()

	track(type='init')
	report_data()

def track(name=None, data=None, type='event'):
	global queue

	if not app_id:
		log_error("set app_id and use app_started() before you can start tracking")

	# Generate a small temp id for this event, so when the server returns it
	# we can remove it from the queue
	temp_id = random.randint(1, 10000)

	event_data = {
		"type": type,
		"name": name,
		"date": datetime.datetime.now().isoformat(),
		"appId": app_id,
		"id": temp_id,
		"userId": user_id,
		"machineId": machine_id,
		"sessionId": session_id,
		"payload": data
	}

	# Extra data is only needed for 1st event and errors,
	# so save bandwidth if not needed

	if (type == 'init' or type == 'error'):

		extra_data = {
			"client": "python",
			"platform": os_name,
			"osVersion": os_version,
			"totalRam": ram,
			"version": version,
			"locale": locale,
			"arch": arch,
			"moduleVersion": module_version
		}

		event_data = merge_dicts(event_data, extra_data)

	queue.append(event_data)
	db.set('queue', queue)

def track_error(e):

	type = e.__class__.__name__
	message = str(e)
	stacktrace= ''.join(traceback.format_tb(e.__traceback__))

	err_object = {
		"message": message,
		"stack": stacktrace
	}

	track(type, data=err_object, type='error')

def set_user_id(new):
	global user_id

	user_id = new

	log('user id set to ' + user_id)
	
	track(type='userid') 

def set_props(new_props, overwrite=False):
	global props, user_id

	if ('user_id' in new_props): 
		user_id = new_props.user_id

	# Merge past and new props
	props = new_props if overwrite else merge_dicts(props, new_props)

	db.set('props', props)
	db.dump()

	track(data=props, type='userid') 

def send_queue():
	if not ws: #or not ws.connected):
		return

	if not len(queue): 
		
		# Nothing to report, send a heartbeat anyway
		# (like if the connection was lost and is back)
		# this is needed to tell the server which user this is
		# only the machine id is needed to derive the other informations
		
		heartbeat = {
			"data": [{
				"event": 'nucleus:heartbeat',
				"machineId": machine_id
			}]
		}

		return ws.send(json.dumps(heartbeat))

	payload = {
		"data": queue
	}

	log('sending cached events ('+str(len(queue))+')')

	try:
		ws.send(json.dumps(payload))
	except: 
		error_log("could not send data. We'll try later.")

def activate_ws():
	global ws

	if not ws:
		# if enable_logs:
		# 	websocket.enableTrace(True)

		protocol = "ws" if dev else "wss"
		endpoint = protocol + "://" + api_url + "/app/" + app_id + "/track"

		try:
			ws = websocket.WebSocketApp(endpoint,
									on_message = on_message,
									on_error = on_error,
									on_close = on_close,
									on_open = on_open )

			# ws.on_open = send_queue()
			ws.run_forever()
		except:
			log_error('could not start websocket connection. Something seems wrong.')

	elif len(queue):
		send_queue()

def on_open(client):
	# time.sleep(2) # let time for connection to establish
	send_queue()

def report_data():
	
	if disable_tracking: return

	thread = threading.Thread(target=activate_ws, daemon=True)
	thread.daemon = True
	thread.start()

def on_message(ws, message):
	global queue

	data = json.loads(message)

	log('new message from server')
	log(message)

	if 'reportedIds' in data:
		log('server successfully registered data')

		try:
			queue = [item for item in queue if item['id'] not in data['reportedIds']]

			db.set('queue', queue)

		except Exception as error:
			log_error(error)

def on_error(client, error):
	global ws
	ws = None

	log_error("Nucleus: error with connection. We'll try again later.")

def on_close(client):
	global ws
	ws = None

	log('websocket connection closed')