import locale, struct, platform
import time, datetime
import threading
import traceback
import random
import json

import websocket
import pickledb
import appdirs

from .utils import get_total_ram, get_machine_id, merge_dicts, generate_user_id

db_path = appdirs.user_cache_dir()

# Non modifiable event data
module_version = "0.3"
machine_id = get_machine_id()

class Client():

	# Init all needed variables
	# Get the user data
	# and load the DB if any

	def __init__(self, 
			app_id=None, 
			debug=False, 
			auto_user_id=False, 
			report_interval=20, 
			disable_tracking=False, 
			api_url='wss://app.nucleus.sh' ):

		if not app_id:
			return self.log_error("missing app_id")

		self.app_id = app_id
		self.debug = debug
		self.api_url = api_url
		self.report_interval = report_interval
		self.disable_tracking = disable_tracking

		self.user_data = {
			'user_id': generate_user_id() if auto_user_id else None,
			'ram': get_total_ram(),
			'arch': struct.calcsize("P") * 8,
			'version': "0.0.0",
			'locale': None,
			'os_name': platform.system(),
			'os_version': platform.release()
		}

		try:
			self.user_data['locale'] = locale.getdefaultlocale()[0]
		except:
			self.log_error('Could not detect user locale (probably the MacOS bug)')

		self.session_id = random.randint(1000, 9999)

		self.ws = None

		# Restore DB
		filename = 'nucleus-' + self.app_id
		self.db = pickledb.load(db_path + '/' + filename, True)
		self.queue = self.db.get('queue') or []
		self.props = self.db.get('props') or {}

		# Regularly run the function to let the server know client is still connected
		timer = threading.Timer(self.report_interval, self.report_data)
		timer.daemon = True
		timer.start()

	def app_started(self):

		self.track(type='init')
		
		# Directly report data so there's no latency with realtime view
		self.report_data()

	def track(self, name=None, data=None, type='event'):

		if self.disable_tracking:
			return

		# Generate a small temp id for this event, so when the server returns it
		# we can remove it from the queue
		temp_id = random.randint(1, 10000)
		date = datetime.datetime.now().isoformat()

		event_data = {
			"type": type,
			"name": name,
			"date": date,
			"appId": self.app_id,
			"id": temp_id,
			"userId": self.user_data['user_id'],
			"machineId": machine_id,
			"sessionId": self.session_id,
			"payload": data
		}

		# Extra data is only needed for 1st event and errors,
		# so save bandwidth if not needed

		if (type == 'init' or type == 'error'):

			extra_data = {
				"client": "python",
				"platform": self.user_data['os_name'],
				"osVersion": self.user_data['os_version'],
				"totalRam": self.user_data['ram'],
				"version": self.user_data['version'],
				"locale": self.user_data['locale'],
				"arch": self.user_data['arch'],
				"moduleVersion": module_version
			}

			event_data = merge_dicts(event_data, extra_data)

		self.log('adding to queue: '+type)

		self.queue.append(event_data)
		self.db.set('queue', self.queue)

	def track_error(self, e):

		type = e.__class__.__name__
		message = str(e)
		stacktrace= ''.join(traceback.format_tb(e.__traceback__))

		err_object = {
			"message": message,
			"stack": stacktrace
		}

		self.track(type, data=err_object, type='error')

	def disable_tracking(self, new):

		self.disable_tracking = True
		self.log('tracking disabled')

	def enable_tracking(self, new):

		self.disable_tracking = False
		self.log('tracking enabled')

	def set_user_id(self, new):

		self.user_data['user_id'] = new
		self.log('user id set to ' + new)
		self.track(type='userid') 

	def set_props(self, new_props, overwrite=False):

		# Overwrite user_data if it's a property of this
		for key, value in new_props.iteritems():
			if self.user_data[key]:
				self.user_data[key] = value

		# Merge past and new props
		self.props = new_props if overwrite else merge_dicts(self.props, new_props)

		self.db.set('props', self.props)
		# self.db.dump()

		self.track(data=self.props, type='userid') 

	def send_queue(self):
		if not self.ws:
			return

		if not len(self.queue): 
			
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
			"data": self.queue
		}

		count = str(len(self.queue))

		self.log('sending cached events: '+count)

		try:
			self.ws.send(json.dumps(payload))
		except: 
			self.log_error("could not send data. We'll try later.")

	def report_data(self):
		
		if self.disable_tracking: 
			return

		thread = threading.Thread(target=self.activate_ws, daemon=True)
		thread.daemon = True
		thread.start()

	def activate_ws(self):

		if not self.ws:
			# if self.debug:
			# 	websocket.enableTrace(True)

			self.log('trying to start ws connection')

			endpoint = self.api_url + "/app/" + self.app_id + "/track"

			# try:
			self.ws = websocket.WebSocketApp(endpoint,
									on_message = self.on_ws_message,
									on_error = self.on_ws_error,
									on_close = self.on_ws_close,
									on_open = self.on_ws_open )

			self.ws.run_forever()

			# except:
				# self.log_error('could not start websocket connection. Something seems wrong.')

		elif len(self.queue):
			self.send_queue()

	def on_ws_open(self):
		self.log('ws connection open')
		self.send_queue()

	def on_ws_message(self, message):

		self.log('new message from server')
		self.log(message)

		data = json.loads(message)

		if 'reportedIds' in data:
			self.log('server successfully registered data')

			try:
				self.queue = [item for item in self.queue if item['id'] not in data['reportedIds']]

				self.db.set('queue', self.queue)

			except Exception as error:
				self.log_error(error)

	def on_ws_error(self, error):
		
		self.log_error("error with ws connection")
		self.ws = None

	def on_ws_close(self):
		
		self.log_error('websocket connection closed')
		self.ws = None

	def log(self, message):

		if (self.debug):
			print('Nucleus: '+message)

	def log_error(self, message):
		
		if (self.debug):
			print('Nucleus error: '+message)
