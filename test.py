import sys, time
import nucleus

nucleus.app_id = '5db75280823739031ec1378c'
nucleus.debug = True
nucleus.api_url = 'ws://localhost:5000'

nucleus.set_props({
	'version': '0.5.0'
})

nucleus.app_started()

# try:
# 	raise Exception('This is the exception you expect to handle')
# except Exception as error:
# 	print(error)
# 	nucleus.track_error(error)

nucleus.track('test_event', data={
	'this': 'isAwesome'
})


time.sleep(4)