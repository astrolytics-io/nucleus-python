from psutil import virtual_memory
import sys, struct, socket, getpass, ssl, datetime, random, json, websocket

# User data
platform = sys.platform
ram = int(virtual_memory().total / 1e9)
arch = struct.calcsize("P") * 8
apiUrl = "app.nucleus.sh"
reportDelay = 20 # s between reportings
hostname = socket.gethostname()
username = getpass.getuser()
machineId = 'test'

disableTracking = False
userId = None
version = None
language = None
dev = False
devMode = False
enableLogs = True

queue = []
props = None
appId = None

ws = None

def init(appId, options):
	sessionId = random.randint(1000, 9999)

	if (options.autoUserId): userId = generateUserId()
	if (options.version): version = options.version
	if (options.language): language = options.language
	if (options.endpoint): apiUrl = options.endpoint
	if (options.devMode): dev = options.devMode
	if (options.enableLogs): enableLogs = options.enableLogs
	if (options.disableTracking): disableTracking = options.disableTracking
	if (options.reportDelay): reportDelay = options.reportDelay
	if (options.userId): userId = options.userId

	track('init')

def autoUserId():
	userId = username + "@" + hostname

def mergeDicts(x, y):
	z = x.copy()
	z.update(y)
	return z

def track(eventName, data):
	tempId = random.randint(1, 10000)

	eventData = {
		"event": eventName,
		"date": datetime.datetime.now(),
		"appId": appId,
		"id": tempId,
		"userId": userId,
		"machineId": machineId,
		"sessionId": sessionId,
		"payload": data
	}

	extraData = {
		"platform": platform,
		"osVersion": osVersion,
		"totalRam": totalRam,
		"version": version,
		"language": language,
		"arch": arch,
		"moduleVersion": moduleVersion
	}

	if ((eventName == 'init') or ('error:' in eventName)):
		eventData = mergeDicts(eventName, extraData)

	queue.append(eventData)

	return

def setUserId(new):
	userId = new
	track('nucleus:userid') 
	return

def setProps (new):
	userId = new
	track('nucleus:userid') 
	return

def disableTracking():
	disableTracking = True

def enableTracking():
	disableTracking = False

def sendQueue():
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
				"machineId": machineId
			}]
		}

		return ws.send(json.dumps(heartbeat))


	payload = {
		"data": queue
	}

	if (enableLogs): 
		print('Nucleus: sending cached events ('+queue.len()+')')

	ws.send(json.dumps(payload))

def reportData():
	websocket.enableTrace(True)

	protocol = "ws" if dev else "wss"
	endpoint = protocol + "://" + apiUrl

	ws = websocket.WebSocketApp(endpoint,
							on_message = onMessage,
							on_error = onError,on_close = onClose)

	ws.on_open = sendQueue
	ws.run_forever()

def onMessage(ws, message):
	print('New message from server')
	print(message)

def onError(ws, error):
	print(error)

def onClose(ws):
	print("### closed ###")

