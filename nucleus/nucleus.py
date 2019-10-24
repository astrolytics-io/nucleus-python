import struct, psutil, socket, hashlib, getpass, getmac, datetime, random, json, websocket, locale, platform

# User data
# Can be overwritten after importing the module
ram = int(psutil.virtual_memory().total / 1e9)
arch = struct.calcsize("P") * 8
api_url = "app.nucleus.sh"
report_delay = 20 # s between reportings
hostname = socket.gethostname()
username = getpass.getuser()
language = locale.getdefaultlocale()[0]
machine_id = hashlib.md5(getmac.get_mac_address().encode('utf-8')).hexdigest()
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
queue = []
props = None
ws = None

def init():
	track('init')

def generate_user_id():
	user_id = username + "@" + hostname

def merge_dicts(x, y):
	z = x.copy()
	z.update(y)
	return z

def track(event_name, data=None):
	if (not app_id):
		return print("Nucleus: app_id needed before you can start tracking")

	# Generate a small temp id for this event, so when the server returns it
	# we can remove it from the queue
	temp_id = random.randint(1, 10000)

	event_data = {
		"event": event_name,
		"date": datetime.datetime.now(),
		"appId": app_id,
		"id": temp_id,
		"userId": user_id,
		"machineId": machine_id,
		"sessionId": session_id,
		"payload": data
	}

	# Extra data is only needed for 1st event and errors,
	# so save bandwidth if not needed

	if ((event_name == 'init') or ('error:' in event_name)):

		extra_data = {
			"platform": os_name,
			"osVersion": os_version,
			"totalRam": ram,
			"version": version,
			"language": language,
			"arch": arch,
			"moduleVersion": module_version
		}

		event_data = merge_dicts(event_data, extra_data)

	queue.append(event_data)

	return

def track_error(e):

	type = e.__class__.__name__
	message = str(e)
	traceback = str(e.__traceback__)

	err_object = {
		"message": message,
		"stack": traceback
	}

	print('type '+type)
	print('message '+message)
	print('stack '+traceback)

	track('error:'+type, err_object)

def set_user_id(new):
	user_id = new
	if (enable_logs): print('Nucleus: user id set to ' + user_id)
	track('nucleus:userid') 
	return

def set_props(new_props, overwrite=False):

	if (new_props.user_id): 
		user_id = new_props.user_id

	# Merge past and new props
	props = new_props if overwrite else merge_dicts(props, new_props)

	track('nucleus:props', props) 
	return

def disable_tracking():
	if (enable_logs): print('Nucleus: tracking disabled')
	disable_tracking = True

def enable_tracking():
	if (enable_logs): print('Nucleus: tracking enabled')
	disable_tracking = False

def send_queue():
	if (not ws or not ws.connected):
		return
	
	if (queue.len() <= 0): 
		
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

	if (enable_logs): 
		print('Nucleus: sending cached events ('+queue.len()+')')

	ws.send(json.dumps(payload))

def report_data():

	if (disable_tracking): return
	
	if (not ws):
		protocol = "ws" if dev else "wss"
		endpoint = protocol + "://" + api_url

		ws = websocket.WebSocketApp(endpoint,
								on_message = on_message,
								on_error = on_error,
								on_close = on_close,
								on_open = send_queue)
		ws.run_forever()

	if (queue.len()): send_queue()

def on_message(ws, message):
	data = json.loads(message)

	if (data.reported_ids or data.confirmation):
		if (enable_logs):
			print('Nucleus: server successfully registered data')
		
		if (data.reported_ids):
			queue = [item for item in queue if item.id not in data.reported_ids]

	if (enable_logs):
		print("Nucleus: new message from server")
		print(message)

def on_error(ws, error):
	ws = None

	if (enable_logs):
		print("Nucleus: error with connection")
		print(error)

def on_close(ws):
	ws = None

	if (enable_logs):
		print("Nucleus: connection closed")
