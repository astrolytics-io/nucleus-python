from setuptools import find_packages, setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
	name='python-nucleus',
	version='0.1.1',
	description='Analytics and bug tracking for Python desktop apps',
	license='MIT License',
	long_description=README,
    long_description_content_type="text/markdown",
	author='Lyser.io',
	author_email='hello@lyser.io',
	packages=find_packages(exclude=("tests",)),
	keywords=['analytics', 'tracking', 'error','bug', 'crash'],
	install_requires=[
		'websocket-client',
		'psutil',
		'getmac',
		'appdirs',
		'pickledb'
	],
	url='https://github.com/lyserio/python-nucleus'
)
