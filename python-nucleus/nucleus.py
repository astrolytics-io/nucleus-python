from psutil import virtual_memory
import sys, struct, socket, getpass


platform = sys.platform
ram = int(virtual_memory().total / 1e9)
arch = struct.calcsize("P") * 8
apiUrl = "app.nucleus.sh"
reportDelay = 20 # s between reportings
disableTracking = False
userId = None
hostname = socket.gethostname()
username = getpass.getuser()

def autoUserId():
	userId = username + "@" + hostname

def track(event, data):
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

print('yo')
print(platform)
print(ram)
print(arch)