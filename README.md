Endpoint
========
[![Build Status](https://travis-ci.org/javidgon/endpoint.png)](https://travis-ci.org/javidgon/endpoint)

**Endpoint is to APIs the same as Unit tests are to the code.**

It's main purpose is to check if your API's endpoints are working properly.
That "proper way" is specified in a .yml file with a defined structure that provides
your specific responses' requirements for each call to Endpoint.

What can it be useful for? Well, let's think about a critical performance web service which
should serve responses within 0.2 seconds. Slower than that should be considerer as unacceptable.
With Endpoint, you can easily specify your requirements and trigger alerts in real time
if they have not met. 

Endpoint supports API calls using **GET**, **POST** and **PUT** methods,
with **Basic** and **Digest AUTH**. Next step will be to include OAuth support as well, as many important
systems are using this protocol.

Currently, It's possible to assert about "status-code" (response's status code) and "waiting-time" (response's timing). 
If any of those assertions doesn't meet with the real response, some things will happen behind the scenes...
First, Endpoint will mark the returned JSON with **tests_passed: False**,
second, some events as email notification will be triggered automatically (though It's fully customizable by the user)
and, finally, the output will inform the user accordingly.

For sake of testing and learning, Endpoint includes both a **mock server** and a **endpoint.yml** example file in the
/tests folder. For running the Test Suite just type: **fab test_suite**

In order to improve the clearness, let's dive into the .yml structure that Endpoint recognizes:

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

> You can easily try this out by typing the following line at the terminal:

```
	curl http://127.0.0.1:5000/get_endpoint
```

> Please note that the server should be running! If it doesn't, just do **python run_app.py <yml_path>**

Output structure
----------------

Endpoint responds you with a JSON obj with the following structure (Using *tests/endpoint.yml* as example):

<pre>
(endpoint)$ curl http://127.0.0.1:5000

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
	fab supervise:yml_file=<yml_path**>, mode:<one_time or strict**>, interval: <60**>, test_mode: <True or False**>
	**: Optional parameter.
	# *By default, the yml_file is the one placed inside the /tests folder,*
	# *the mode is 'one_time', interval is set to 60 and test_mode is False.*
	
	Examples:
	
	fab supervise:yml_file=endpoint.yml, mode=strict, interval=10 # Check every 10 seconds
	fab supervise:yml_file=endpoint.yml 						  # Check just a single time
```

* You probably have noticed that we have a mode parameter with two possible values.
	* 'one_way': Check all the endpoints a single time (Interval param not used)
	* 'strict': Check all the endpoints regularly every <interval> seconds. Isn't it great?
	
**2. Manual flavor.**

* Runs the server and nothing else. You can then start either using tools as **'curl'** or simply
  accessing to **http://127.0.0.1:5000** at your favorite browser.
  
```
	python run_app.py <yml_path>
``` 
  
Tests
-----

As we mentioned before, you can run the **Endpoint's Test Suite** just by typing:

```
	fab test_suite
```
> It will use both the endpoint.yml file from the tests/ folder and the mock server.

You should get then something similar to:

<pre>

127.0.0.1 - - [01/Jan/2013 16:58:54] "POST /mock/post/digest-auth HTTP/1.1" 401 -
.127.0.0.1 - - [01/Jan/2013 16:58:54] "GET /mock HTTP/1.1" 301 -
127.0.0.1 - - [01/Jan/2013 16:58:54] "GET /mock/ HTTP/1.1" 200 -
...
----------------------------------------------------------------------
Ran 14 tests in 0.951s

OK
[localhost] local: pkill -n python run_mock.py

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

BSD LICENSE
-------

Copyright (c) 2012 by Jose Vidal and AUTHORS (further information in AUTHORS file).

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

    * The names of the contributors may not be used to endorse or
      promote products derived from this software without specific
      prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
