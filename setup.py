from setuptools import setup

setup(
	name='python-nucleus',
	version='0.1.0',
	description='Analytics and bug tracking for Python desktop apps',
	license='MIT',
	packages=['nucleus'],
	author='Lyser.io',
	author_email='hello@lyser.io',
	keywords=['analytics', 'tracking', 'error','bug', 'crash'],
	install_requires=[
		'websocket',
		'psutil',
		'getmac',
		'appdirs',
		'pickledb'
	],
	url='https://github.com/lyserio/python-nucleus'
)