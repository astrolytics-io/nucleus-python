import hashlib, getmac, psutil, getpass, socket

def generate_user_id():
	hostname = socket.gethostname()
	username = getpass.getuser()
	user_id = username + "@" + hostname

def merge_dicts(x, y):
	z = x.copy()
	z.update(y)
	return z

def get_machine_id():
	return hashlib.md5(getmac.get_mac_address().encode('utf-8')).hexdigest()

def get_total_ram():
	return int(psutil.virtual_memory().total / 1e9)
