# nucleus-python ![PyPI](https://img.shields.io/pypi/v/nucleus-python) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nucleus-python) 

We tried to make it as simple as possible to report the data you need to analyze your app usage and improve it.

This module is compatible with Python 3+.

To start using this module, sign up and get an app ID on [Nucleus.sh](https://nucleus.sh). 

## Installation

```bash
$ pip install nucleus-python
```

## Basic usage

Add the following code to import Nucleus and init the analytics.

Don't use the `import ... from` syntax as you won't be able to set the module options like `app_id`.


```python
import nucleus

nucleus.app_id = 'your app id'

nucleus.set_props({
	'version': '0.5.0', # Set app version (Nucleus cannot detect it)
	'userId': 'richard_hendrix'
})

nucleus.app_started()
```

**Only use `app_started()` once per session, if you are using Nucleus in several files call app_started() the earliest possible.**

Sign up and get a tracking ID for your app [here](https://nucleus.sh).

### Options

You can init Nucleus with options:

```python
nucleus.report_interval = 20 # interval (in seconds) between server com
nucleus.disable_tracking = False # completely disable tracking
nucleus.debug = False # Show internal logs to help debug
nucleus.auto_user_id = False # Assign the user an ID
```

### Identify users

You can track specific users actions on the 'User Explorer' section of your dashboard by assigning an user ID. 

It can be any value as long as it is a *string*.

```python
nucleus.set_user_id('someUniqueUserId')
```

Alternatively, set the `auto_user_id` option of the module to `True` to automatically assign the user an ID based on his username and hostname.

### Modify automatic data

You can overwrite some properties or fill data that wasn't detected.

*You have to do it before calling `app_started()` for this to work*

It is a good idea to set your app version directly as Nucleus **cannot detect it** for the moment.

```python
nucleus.set_props({
	'version': '0.5.0',
	'locale': 'en_US'
})
```

### Track custom data

You can also add custom data along with the automatic data.
 
Those will be visible in your user dashboard *if you previously set an user ID*.

The module will remember past properties so you can use `nucleus.set_props` multiple times without overwriting past props.

Properties can either **numbers**, **strings** or **booleans**. 
Nested properties or arrays aren't supported at the moment.

```python
nucleus.set_props({
	"age": 34,
	"name": 'Richard Hendricks',
	"job": 'CEO'
})
```

To overwrite past properties, set the second parameter to `True`. 

```python
nucleus.set_props({
	"age": 23
}, True)
```

### Errors

To catch errors with Nucleus, simply add the tracking code to an exception and pass the exception as the unique parameter. 

Nucleus will extract the relevant informations and show them in your dashboard.

```python
try:
    my_app()
except Exception as e:
	nucleus.track_error(e)
```

Add this at the outermost level of your code to handle any otherwise uncaught exceptions before terminating.

The advantage of except Exception over the bare except is that there are a few exceptions that it wont catch, most obviously KeyboardInterrupt and SystemExit.


### Events

After initializing Nucleus, you can send your own custom events.

```python
nucleus.track("PLAYED_TRACK")
```

They are a couple event names that are reserved by Nucleus: `init`, `error:` and `nucleus:`.

You shouldn't report events containing these strings.

#### Tracking with data

You can add extra information to tracked events, as an object.

Properties can either **numbers**, **strings** or **booleans**. 

Nested properties or arrays aren't supported at the moment.

Example:

```python
nucleus.track("PLAYED_TRACK", data = {
	"trackName": 'My Awesome Song',
	"duration": 120
})
```

### Toggle tracking

This will completely disable any communication with Nucleus' servers.

To opt-out your users from tracking:

```python
nucleus.disable_tracking()
```

and to opt back in:

```python
nucleus.enable_tracking()
```

This doesn't persist after restarts so you have to handle saving the setting.

---
Contact **hello@nucleus.sh** for any inquiry
