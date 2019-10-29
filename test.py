import sys, time

sys.path.insert(1, '../nucleus/python-nucleus/nucleus/')

import nucleus

nucleus.version = '0.0.5'
nucleus.user_id = 'test'
nucleus.app_id = '5db75280823739031ec1378c'
nucleus.debug = True
nucleus.dev = True
nucleus.api_url = 'localhost:5000'

nucleus.init()

# try:
# 	raise Exception('This is the exception you expect to handle')
# except Exception as error:
# 	print(error)
# 	nucleus.track_error(error)

nucleus.track('yo', data={
	'this': 'isAwesome'
})


time.sleep(4)