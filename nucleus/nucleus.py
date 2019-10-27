import struct, threading, pickledb, socket, appdirs, getpass, datetime, random, json, websocket, locale, platform

from utils import get_total_ram, get_machine_id, merge_dicts, generate_user_id

# User data
# Can be overwritten after importing the module
ram = get_total_ram()
arch = struct.calcsize("P") * 8
api_url = "app.nucleus.sh"
report_interval = 20 # s between reportings
hostname = socket.gethostname()
username = getpass.getuser()
locale = locale.getdefaultlocale()[0]
machine_id = get_machine_id()
session_id = random.randint(1000, 9999)
os_name = platform.system()
os_version = platform.release()
module_version = "0.0.1"

# Options
app_id = None
disable_tracking = False
user_id = None
version = None
language = None
dev = False
dev_mode = False
enable_logs = True

# Cache
db = None
queue = None
props = None
ws = None

def init():
	global db, queue, props

	if (not app_id):
		return print("Nucleus: app_id needed before you can start tracking")

	db_path = appdirs.user_cache_dir()
	filename = 'nucleus-'+app_id
	print(db_path)

	# Restore DB
	db = pickledb.load(db_path + '/' +filename, True)
	queue = db.get('queue') or []
	props = db.get('props') or {}

	track(type='init')

def track(name=None, data=None, type='event'):
	global queue

	if (not app_id):
		return print("Nucleus: set app_id and use init() before you can start tracking")

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
	traceback = str(e.__traceback__)

	err_object = {
		"message": message,
		"stack": traceback
	}

	track(data=err_object, type='error')

def set_user_id(new):
	global user_id

	user_id = new
	if (enable_logs): print('Nucleus: user id set to ' + user_id)
	track(type='userid') 

def set_props(new_props, overwrite=False):
	global props, user_id

	if (hasattr(new_props, 'user_id')): 
		user_id = new_props.user_id

	# Merge past and new props
	props = new_props if overwrite else merge_dicts(props, new_props)

	db.set('props', props)

	# print(db.get('props'))

	track(data=props, type='userid') 

def send_queue():
	if (not ws or not ws.connected):
		return
	
	if (queue.count() <= 0): 
		
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
		"data": queue.all()
	}

	if enable_logs:
		print('Nucleus: sending cached events ('+queue.count()+')')

	ws.send(json.dumps(payload))

def report_data():
	global ws

	# Regularly run the function to let the server know client is still connected
	threading.Timer(report_interval, report_data).start()

	if disable_tracking: return
	
	if not ws:
		protocol = "ws" if dev else "wss"
		endpoint = protocol + "://" + api_url

		ws = websocket.WebSocketApp(endpoint,
								on_message = on_message,
								on_error = on_error,
								on_close = on_close,
								on_open = send_queue)
		ws.run_forever()

	if (queue.count()): send_queue()

def on_message(ws, message):
	global queue

	data = json.loads(message)

	if (data.reported_ids or data.confirmation):
		if enable_logs:
			print('Nucleus: server successfully registered data')
	
		if data.reported_ids:
			queue = [item for item in queue if item.id not in data.reported_ids]
			db.set('queue', queue)

	if enable_logs:
		print("Nucleus: new message from server")
		print(message)

def on_error(ws, error):
	ws = None

	if enable_logs:
		print("Nucleus: error with connection")
		print(error)

def on_close(ws):
	ws = None

	if enable_logs:
		print("Nucleus: connection closed")
