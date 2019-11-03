from .client import Client

# Options
app_id = None
api_url = 'wss://app.nucleus.sh'
report_interval = 20
disable_tracking = False
auto_user_id = False
debug = False

current_client = None

def app_started(*args, **kwargs):
	_proxy('app_started', *args, **kwargs)

def track(*args, **kwargs):
	_proxy('track', *args, **kwargs)

def track_error(*args, **kwargs):
	_proxy('track_error', *args, **kwargs)

def set_props(*args, **kwargs):
	_proxy('set_props', *args, **kwargs)

def set_user_id(*args, **kwargs):
	_proxy('set_user_id', *args, **kwargs)

def disable_tracking(*args, **kwargs):
	_proxy('disable_tracking', *args, **kwargs)

def enable_tracking(*args, **kwargs):
	_proxy('enable_tracking', *args, **kwargs)

def _proxy(method, *args, **kwargs):
	
	"""Create an analytics client if one doesn't exist and send to it."""

	global current_client
	if not current_client:
		
		if not app_id:
			raise TypeError("Missing app_id before we can start tracking.")

		current_client = Client(app_id, api_url=api_url, auto_user_id=auto_user_id, report_interval=report_interval, debug=debug)

	fn = getattr(current_client, method)
	fn(*args, **kwargs)