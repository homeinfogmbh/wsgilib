# wsgilib
An object-oriented WSGI framework based on [flask](http://flask.pocoo.org/docs/0.12/).

## Copyright
Copyright 2017 HOMEINFO - Digitale Informationssysteme GmbH

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Usage
Following are some example use cases.

### Examples
#### Simple WSGI application
A simple WSGI application may be implemented using the `Application` class.

The following example shows a trivial WSGI application that will return the UTF-8 String *"Hello world!"* on any HTTP *GET* request.

    from wsgilib import Application, OK

    application = Application('MyApplication')

    @application.route('/')
    def hello_world(self):
        return OK('Hello world!')


#### ReST Application
For applications using **Re**presentational **S**tate **T**ransfer you can use the same routing idioms as with *flask*.

    from math import factorial
    from wsgilib import Application, Error, OK

    APPLICATION = Application('factorial')

    @APPLICATION.route('/factorial/<int:value>')
    def get_factorial(value):
        """Calculates and returns the factorial of the given number."""
        if value > 100:
            raise Error(f'Value too large: {value}.')

        return OK(f'{value}! = {factorial(value)}')

The above ReST application will return the following response:
* `http://<host>/factorial/12` → *12! = 479001600*

### Return values
The framework provides return value classes to represent common data types.

#### Response
The class `Response` provides the very basic interface to handle responses from the server.  
It is a composition of the `flask.Response` and `Exception` class.  
All `Response` instances thus can be *risen* as exceptions in the code, ultimately being handled as return values by the respective `Application`.

#### Plain Text
To return simple plain text responses, there is the class `PlainText`.

However, this class should not be used directly, since it is being inherited by both `OK` and `Error`.
Those two classes check the HTTP status code provided during their instantiation and can easily be identified as success / error conditions when reading the source code.

#### XML
To automatically convert [PyXB](https://github.com/pabigot/pyxb) DOMs to XML responses, the framework provides the class `XML`.

#### JSON
To automatically return JSON responses from dictionaries, there is a class `JSON`.

#### Binaries
To return binary data, the class `Binary` uses the library [mimeutil](https://github.com/HOMEINFO/mimeutil) to try to detect the appropriate MIME type.

#### Internal server errors
For debugging purposes or to detect runtime errors within a productive system, the class `InternalServerError` can be used.

## Dependencies
* [fancylog](https://github.com/HOMEINFO/fancylog)
* [mimeutil](https://github.com/HOMEINFO/mimeutil)
* [strflib](https://github.com/HOMEINFO/strflib)
* [xmldom](https://github.com/HOMEINFO/xmldom)
