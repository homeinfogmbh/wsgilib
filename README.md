# wsgilib
A simple (U)WSGI framework.

## About
*wsgilib* aims to provide a simple (U)WSGI framework.

### Simple WSGI application
A simple WSGI application may be implemented using the `RequestHandler` and a `WsgiApp` using it.

The following example shows a trivial WSGI application that will return the UTF-8 String *"Hello world!"* on any HTTP *GET* request.

    from wsgilib import OK, RequestHandler, WsgiApp


    class MyHandler(RequestHandler):

        def get(self):
            return OK('Hello world!')


    application = WsgiApp(MyHandler)


### ReST Application
For applications using **Re**presentational **S**tate **T**ransfer the library provides the classes `RestApp`, `RestHandler` and `Router` to handle the respective resources.

    from math import factorial
    from wsgilib import OK, Router, RestHandler, RestApp


    ROUTER = Router()


    @ROUTER.route('/factorial/<value:int>')
    class MyHandler(RestHandler):

        def get(self):
            value = self.vars['value']
            return OK('{}! = {}'.format(value, factorial(value)))


    application = RestApp(ROUTER)

The above ReST application will return the following response:
* `http://<host>/factorial/12` → *"12! = 479001600"*

## Return values
The framework provides return value classes to represent common data types.

### Plain Text
To return simple plain text responses, there is the class `PlainText`.

However, this class should not be used directly, since it is being inherited by both `OK` and `Error`.
Those two classes check the HTTP status code provided during their instantiation and can easily be identified as success / error conditions when reading the source code.

### XML
To automatically convert [PyXB](https://github.com/pabigot/pyxb) DOMs to XML responses, the framework provides the class `XML`.

### JSON
To automatically return JSON responses from dictionaries, there is a class `JSON`.

### Binaries
To return binary data, the class `Binary` uses the library [mimeutil](https://github.com/HOMEINFO/mimeutil) to try to detect the appropriate MIME type.

### Internal server errors
For debugging purposes or to detect runtime errors within a productive system, the class `InternalServerError` can be used.

## Dependencies
* [fancylog](https://github.com/HOMEINFO/fancylog)
* [mimeutil](https://github.com/HOMEINFO/mimeutil)
* [strflib](https://github.com/HOMEINFO/strflib)
* [xmldom](https://github.com/HOMEINFO/xmldom)

# Copyright
Copyright (C) 2017  HOMEINFO - Digitale Informationssysteme GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
