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
For applications using **Re**presentational **S**tate **T**ransfer the library provides the classes `RestApp` and `ResourceHandler` to handle the respective resources.

    from math import factorial
    from wsgilib import Error, OK, ResourceHandler, RestApp


    class MyHandler(ResourceHandler):

        def get(self):
            if self.resource is None:
                return OK('No resource specified.')
            else:
                try:
                    integer = int(self.resource)
                except ValueError:
                    raise Error('Not an integer: {}'.format(self.resource)) from None
                else:
                    return OK('{}! = {}'.format(integer, factorial(integer)))


    HANDLERS = {
        'factorial': ResourceHandler
    }


    application = RestApp(HANDLERS)

The example above of a simple ReST application will return the following values:
* `http://<host>/factorial` → *"No resource specified."*
* `http://<host>/factorial/not_an_integer` → *"Not an integer: not_an_integer"*
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
