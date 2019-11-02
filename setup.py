from setuptools import find_packages, setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
	name='nucleus-python',
	python_requires='>3.1',
	version='0.2.1',
	description='Analytics and bug tracking for Python desktop apps',
	license='MIT License',
	long_description=README,
    long_description_content_type="text/markdown",
	author='Nucleus.sh',
	author_email='hello@nucleus.sh',
	packages=find_packages(exclude=("tests",)),
	keywords=['analytics', 'tracking', 'error','bug', 'crash'],
	install_requires=[
		'websocket-client',
		'psutil',
		'getmac',
		'appdirs',
		'pickledb'
	],
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	url='https://github.com/nucleus-sh/nucleus-python'
)
