Endpoint
========
[![Build Status](https://travis-ci.org/javidgon/endpoint.png)](https://travis-ci.org/javidgon/endpoint)

**Smart testing framework for APIs**

The Endpoint's main goal is to check if your API's endpoints are working properly.
That "proper way" is specified in a *Specification file* with a defined structure that will work
as a "strict sentinel" that supervises your responses' requirements.

Endpoint supports API calls using **GET**, **POST** and **PUT** methods,
with **Basic** and **Digest AUTH**. Next step will be to include OAuth support as well, as many important
systems are using this protocol.

The *Specification file* defines a set of "assertions" as we do it in a normal Unit test function.
Currently, It's possible to assert about **"status-code" (response's status code)** and
**"waiting-time" (response's timing)**.

If any of those assertions doesn't meet with the real response, some things will happen behind the scenes...
First, Endpoint will mark immediately the returned JSON with **tests_passed: False**,
second, some events as email notification will be triggered automatically (It's fully customizable by the user though)
and, finally, the output will inform the user accordingly.

For sake of testing and learning, Endpoint includes both a **mock server** and a **tests.yml** example file.
For running the Test Suite just type: **fab test_suite**

Let's dive into the specification file's structure:

```yaml
# Endpoints declaration.

   - url: "http://127.0.0.1:5100/mock" # URL to check.
     alias: get_endpoint # Alias, the call will be referenced by this name.
     method: GET # Request method.
     auth: # Auth configuration.
       type: basic # basic, digest or False if it doesn't apply.
       user: dev # False if it doesn't apply.
       pass: example # False if it doesn't apply.
     config:
       request-body: False # Request body, False if doesn't apply.
       retries: 3 # Number of retries in case of failure.
     asserts:
       status-code: 200 # Expected status code.
       waiting-time: 0.5 # Should take less than 0.5 seconds.
```
> These files will be stored in the **specs/** folder, so the server can find them later on.

> You can easily try these endpoints out by typing the following line in the CLI:

```
	curl http://127.0.0.1:5000/<spec_file>/
```
> Note that you also can get one single endpoint by doing:
```
	curl http://127.0.0.1:5000/<spec_file>/<endpoint_alias>
```
> Wait, the server should be running! If it doesn't, just do **python run_server.py**

Output structure
----------------

Endpoint will respond you with a JSON object with the following structure:

<pre>
(endpoint)$ curl http://127.0.0.1:5000/tests/

[{"status_code": 200, "url": "http://127.0.0.1:5100/mock/", "method": "GET", "tests_passed": true,
 "requested_at": "2013-01-01 17:13:54.240333"}, {"status_code": 200, "url": "http://127.0.0.1:5100/mock/post",
 "method": "POST", "tests_passed": true, "requested_at": "2013-01-01 17:13:54.244008"}, {"status_code": 200,
 "url": "http://127.0.0.1:5100/mock/post/basic-auth", "method": "POST", "tests_passed": true, 
 "requested_at": "2013-01-01 17:13:54.248098"}, {"status_code": 200, "url": "http://127.0.0.1:5100/mock/post/digest-auth", 
 "method": "POST", "tests_passed": true, "requested_at": "2013-01-01 17:13:54.254822"}, {"status_code": 401, 
 "url": "http://127.0.0.1:5100/mock/post/basic-auth", "method": "POST", "tests_passed": true, 
 "requested_at": "2013-01-01 17:13:54.257857"}, {"status_code": 401, "url": "http://127.0.0.1:5100/mock/post/digest-auth", 
 "method": "POST", "tests_passed": true, "requested_at": "2013-01-01 17:13:54.263823"}, {"status_code": 200, "url": 
 "http://127.0.0.1:5100/mock/put/1", "method": "PUT", "tests_passed": true, "requested_at": "2013-01-01 17:13:54.266956"}, 
 {"status_code": 500, "log": "SERVER_UNREACHABLE", "tests_passed": true, "requested_at": "2013-01-01 17:13:54.268079"}, 
 {"status_code": 400, "log": "BAD_REQUEST", "tests_passed": true, "requested_at": "2013-01-01 17:13:54.268165"}, 
 {"status_code": 408, "log": "REQUEST_TIMEOUT", "tests_passed": true, "requested_at": "2013-01-01 17:13:54.269429"}, 
 {"status_code": 501, "log": "NOT_IMPLEMENTED", "tests_passed": true, "requested_at": "2013-01-01 17:13:54.269556"}]
</pre>

API
---
Endpoint supports both automatic and manual flavors.

**1. Automatic flavor.**

* Lets you test all your API on a painless and automate way, just by typing:

```
	fab supervise:spec_file=<spec_file**>, endpoint:<endpoint_alias**>, mode=<one_time or strict**>, interval=<60**>, test_mode=<True or False**>
	**: Optional parameter.
	# *By default, if no other spec_file has been provided, endpoint will use tests.yml.*
	# *If the 'endpoint' parameter is empty, all the endpoints of that specification file will be tested.*
	
	Examples:
	
	fab supervise:spec_file=tests, endpoint=get_shopping_cart, mode=strict, interval=10 # Check every 10 seconds
	fab supervise:spec_file=tests, endpoint=get_user							  		# Check just a single time
```

* You probably have noticed that we have a mode parameter with two possible values.
	* 'one_way': Check all the endpoints a single time (Interval param not used)
	* 'strict': Check all the endpoints regularly every <interval> seconds. Isn't it great?
	
**2. Manual flavor.**

* Runs the server and nothing else. You can then start either using tools as **'curl'** or simply
  accessing to **http://127.0.0.1:5000** at your favorite browser.
  
```
	python run_server.py
``` 

* Just run the server and nothing else. You can then start either using tools as **'curl'** or simple
  accessing to **http://127.0.0.1:5000/<spec_file>/<endpoint_alias>** at your favorite browser.
  
Tests
-----

As we mentioned before, you can run the **Endpoint's Test Suite** just by typing:

```
	fab test_suite
```
> It will use both the **tests.yml** file from the specs/ folder and the mock server.

You should get then something similar to:

<pre>

127.0.0.1 - - [01/Jan/2013 16:58:54] "POST /mock/post/digest-auth HTTP/1.1" 401 -
.127.0.0.1 - - [01/Jan/2013 16:58:54] "GET /mock HTTP/1.1" 301 -
127.0.0.1 - - [01/Jan/2013 16:58:54] "GET /mock/ HTTP/1.1" 200 -
...
----------------------------------------------------------------------
Ran 14 tests in 0.951s

OK

</pre>

Making of
---------

Endpoint has been created using **Werkzeug**, which provides all the logic behind the routing process,
the **Requests** library, in charge of making all the requests to the different enpoints,
and **Fabric**, which comes in handy in the verification process«s automation.

Please visit each project for further information.

Contributing
------------

If you'd like to contribute, just Fork the repository, create a branch with your changes and send a pull request. 
Don't forget appending your name to AUTHORS ;)

---

*Sunday, 6th January 2013*

