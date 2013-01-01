Endpoint
========
[![Build Status](https://travis-ci.org/javidgon/endpoint.png)](https://travis-ci.org/javidgon/endpoint)

**Endpoint is for APIs the same as a CI system is for Unit tests.**
It's main purpose is to check if the API's endpoints are working on the proper way.
That "proper way" is specified in a .yml file with a defined structure that will work
as a "strict sentinel" that supervises our specific responses' requirements.

At the time of the 0.1 version, Endpoint supports API calls using **GET**, **POST** and **PUT** methods,
with **Basic** and **Digest AUTH**. Next step will be to include OAuth support as well, as many important
systems are using this protocol.

As we said before, Endpoint allows us to easily check the "validity" of a response by matching
the results with the mentioned .yml file. This file specify a set of "assertions" defined by us, 
as we do it at the normal Unit tests methods. Currently, It's possible to assert about "status-code"
(response's status code) and "waiting-time" (response's timing). 
If any of those assertions doesn't meet with the real response, some things will happen behind the scenes...
First, Endpoint will mark it immediately with **tests_passed: False** in the returned JSON,
second, some events as email notification will be triggered automatically (though It's fully customizable by the user)
and, finally, the output will inform the user accordingly.

For sake of testing and learning, Endpoint includes both a **mock server** and a **endpoint.yml** example file in the
/tests folder. For running the Test Suite just type: **fab test_suite**

In order to improve the clearness, let's dive into the .yml structure:

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

> Please note(second time) that if any of those assertions fails, that call will be marked as **tests_passed: False** in the JSON obj.
You can easily try this out by typing the following line at the terminal:

```
	curl http://127.0.0.1:5000/get_endpoint
```

> Please note that the server should be running! If it doesn't, just do **python run_app.py <yml_path>**

Output structure
----------------

Endpoint will respond you with a JSON obj with the following structure (Using *tests/endpoint.yml* as example):

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
Endpoint has both automatic and manual mode. Let's discover them!

**1. Automatic mode.**

* This mode lets you test all your API on a painless way, just by typing:

```
	fab supervise:yml_file=<yml_path**>, mode:<one_time or strict**>, interval: <60**>, test_mode: <True or False**>
	**: Optional parameter.
	# *By default, the yml_file is the one placed inside the /tests folder,*
	# *the mode is 'one_time', interval is set to 60 and test_mode is False.*
	
	Examples:
	
	fab supervise:yml_file=endpoint.yml, mode=strict, interval=10 # Check every 10 seconds
	fab supervise:yml_file=endpoint.yml 						  # Check just a single time
```

* You probable have noticed that we have a mode parameter with two possible values, what's all this about?
	* 'one_way': Check all the endpoints a single time (Interval param is not used)
	* 'strict': Check all the endpoints regularly every <interval> seconds. Isn't it great?
	
**2. Manual mode.**

* This mode just runs the server and let you the responsibility of asking to the Endpoint server.
  We saw an example of this above:
  
```
	python run_app.py <yml_path>
``` 

* Just run the server and nothing else. You can then start either using tools as **'curl'** or simple
  accessing to **http://127.0.0.1:5000** at your favorite browser.
  
Tests
-----

As we mentioned before, you can run the **Endpoint's Test Suite** just by typing:

```
	fab test_suite
```
> It will use both the endpoint.yml file from the tests/ folder and the mock server.

You should get then something like:

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
---

BSD LICENSE
-------

Copyright (c) 2012 by Jose Vidal.

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
