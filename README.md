# wsgilib
An extended WSGI framework based on [flask](http://flask.pocoo.org/docs/0.12/).

## Usage
Following are some example use cases.

### Examples
The `Application` class takes three special parameters that `Flask` does not.  
The flag `cors` can be used to set the Cross-Origin Resource Sharing settings.  
If `debug` is set, unhandled exceptions will result in the return of a full stack trace.  

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
All `Response` instances thus can be *raised* as exceptions in the code, ultimately being handled as return values by the respective `Application`.  
The default status of `Response` is `200`.

#### Plain Text
To return simple plain text responses, there is the class `PlainText`.

However, this class should not be used directly, since it is being inherited by both `OK` and `Error`.
Those two classes check the HTTP status code provided during their instantiation and can easily be identified as success / error conditions when reading the source code.

##### OK
Retuns a plain text success message. The default status is `200`. Valid values are 200-299.

##### Error
Retuns a plain text error message. The default status is `400`. Valid values are 400-599.

#### XML
The framework provides the class `XML` for returning XML text.  
It automatically detects and converts [PyXB](https://github.com/pabigot/pyxb) DOMs and `xml.etree.ElementTree.Element`s to XML text.

    dom = MY_BINDING.CreateFromDocument(XML_TEXT)

    @APPLICATION.route('/xml')
    def get_xml():
        """Returns an XML text response from a PyXB DOM."""
        return XML(dom)
        
or

    from xml.etree.ElementTree import Element, SubElement
    
    root = Element('root', attrib={'foo': '42'})
    sub_element = SubElement(root, 'bar', attrib={'spamm': 'eggs'})
    sub_element.text = 'Hello world.'

    @APPLICATION.route('/xml')
    def get_xml():
        """Returns an XML text response from an Element object."""
        return XML(root)

The latter example will result in `<root foo="42"><bar spamm="eggs">Hello world.</bar></root>`.

#### JSON
To automatically return JSON responses from `dict`s, there is a class `JSON`:

    @APPLICATION.route('/json')
    def get_json():
        """Returns a JSON object as described by the dictionary."""
        json = {
            'id': 12,
            'name': 'my_object',
            'success': True,
            'issued': datetime.now()
        }
        return JSON(json)

#### Binaries
To return binary data, the class `Binary` uses the library [mimeutil](https://gitlab.com/HOMEINFO/mimeutil) to try to detect the appropriate MIME type:

    @APPLICATION.route('/binary')
    def get_binary():
        """Returns a binary file.
        You can optionally specify the file's name
        via the URL parameter <filename>.
        """
        with open('/my/file', 'rb') as file:
            return Binary(file.read(), filename='my_file.bin')

#### Internal server errors
For debugging purposes or to detect runtime errors within a productive system, the class `InternalServerError` can be used.

### Cross-Origin Resource Sharing
To use CORS, you can spcify the keyword argument `cors` when instantiating `Application`.  
The following values are accepted:

* `None` (default) or `False` to disable CORS
* `True` to enable CORS for any origin.
* A `dict` to manually set the CORS parameters:

```
{
    "origins": [
        "https://my.domain.com",
        "https://otherdomain.org"
    ],
    "methods": [
        "OPTIONS",
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ],
    "headers": [
        "Content-Type",
        "Cache-Control",
        "X-Requested-With",
        "Authorization",
        "session-duration"
    ],
    "credentials": true
}
```

The keys are used as follows:
* `origins`: List of allowed `origin`s headers for `Access-Control-Allow-Origin`.
* `methods`: Allowed methods for `Access-Control-Allow-Methods`.
* `headers`: Allowed headers for `Access-Control-Allow-Headers`.
* `credentials`: Sets `Access-Control-Allow-Credentials` to `"true"` if `True`ish.

## Copyright
Copyright (C) 2017-2021 HOMEINFO - Digitale Informationssysteme GmbH <info at homeinfo period de>

wsgilib is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

wsgilib is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with wsgilib.  If not, see <http://www.gnu.org/licenses/>.

## Dependencies
* [mimeutil](https://github.com/homeinfogmbh/mimeutil)
