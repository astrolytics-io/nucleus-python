from setuptools import setup

setup(
	name='python-nucleus',
	version='0.0.1',
	description='Analytics and bug tracking for python applications',
	license='MIT',
	packages=['python-nucleus'],
	author='Vince Lwt',
	author_email='vince@lyser.io',
	keywords=['analytics'],
	install_requires=[
		'websockets',
		'asyncio',
		'psutil',
		'getpass'
	],
	url='https://github.com/lyserio/python-nucleus'
)