# nucleus-python ![PyPI](https://img.shields.io/pypi/v/python-nucleus) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-nucleus) 

We tried to make it as simple as possible to report the data you need to analyze your app and improve it.

To start using this module, sign up and get an app ID on the [Nucleus website](https://nucleus.sh). 

## Installation

```bash
$ pip install python-nucleus
```

## Usage

Add the following code to import Nucleus and init the analytics.

Don't use the `import ... from` syntax as you won't be able to access inside module variables.


```python
import nucleus

nucleus.app_id = 'your app id'
nucleus.version = '1.3.9'

nucleus.init()
```

**Only use `init()` once per session, if you are using Nucleus in several files call init() the soonest possible.**

Sign up and get a tracking ID for your app [here](https://nucleus.sh).

### Options

You can init Nucleus with options:

```python
nuclesu.report_interval = 20 # interval (in seconds) between server com
nucleus.disable_tracking = False # completely disable tracking
nucleus.user_id = 'user123' # set an identifier for this user
nucleus.debug = False # Show internal logs to help debug
nucleus.version = '1.3.9' # set the current version of your app
nucleus.locale = 'es_ES' # specify a custom locale (default: autodetected)
```

By default **language** is autodetected but you can overwrite it.


### Identify your users

You can track specific users actions on the 'User Explorer' section of your dashboard.

For that, you can supply an `userId` when initing the Nucleus module. 

It can be your own generated ID, an email, username... etc.

```python
nucleus.user_id = 'someUniqueUserId'

nucleus.init()
```

Or if you don't know it on start, you can add it later with:

```python
nucleus.set_user_id('someUniqueUserId')
```

Alternatively, set the `autoUserId` option of the module to `True` to automatically assign the user an ID based on his username and hostname.


### Track custom data

You can add custom data along with the automatic data.
 
Those will be visible in your user dashboard *if you previously set an user ID*.

The module will remember past properties so you can use `nucleus.set_props` multiple times without overwriting past props.

Properties can either **numbers**, **strings** or **booleans**. 
Nested properties or arrays aren't supported at the moment.

```python
nucleus.set_props({
	"age": 34,
	"name": 'Richard Hendricks',
	"jobType": 'CEO'
})
```

Enable overwrite: set the second parameter as `True` to overwrite past properties. 

```python
nucleus.set_props({
	"age": 23
}, True)
```

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
nucleus.disable_tracking = True
```

and to opt back in:

```python
nucleus.disable_tracking = False
```

This change won't persist after restarts so you have to handle the saving of the settings.


### Errors

To track errors with Nucleus, simply add the tracking code to an exception and pass the exception as the unique parameter. 

Nucleus will extract the relevant informations and show them in your dashboard.

```python
try:
    my_app()
except Exception as e:
	nucleus.track_error(e)
```

Add this at the outermost level of your code to handle any otherwise uncaught exceptions before terminating.

The advantage of except Exception over the bare except is that there are a few exceptions that it wont catch, most obviously KeyboardInterrupt and SystemExit.


---
Contact **hello@nucleus.sh** for any inquiry
