# **bb_json_classes**

This is a small set of helper functions to make the job of creating objects (courses, announcements, etc.) with the Blackboard Learn REST APIs slightly easier. Using the APIs is easy enough, but constructing the required JSON bodies can be a little fiddly.  

What this enables you to do is automatically read Blackboard's Swagger JSON for their APIs and automatically generate Python classes for any POST method that requires parameters in JSON form.

I may make this a proper Python package at some point, but for now you can use this by dropping this file into your project and installing the dependencies in requirements.txt.

### Usage

`from bb_json_classes import get_json_classes`

`json_classes = get_json_classes()`

(You can optionally specify an API version. E.g., `json_classes = get_json_classes('3800.17.0')`.) 

You'll now have a dictionary (json_classes) with class name placeholders as the keys and the constructor functions as values. The names are currently constructed by using the summary field in the Swagger specification, removing whitespace, and adding JSON--e.g., 'CreateCourseJSON'. You can then construct your objects either directly out of the class dictionary:

`course = classes['CreateCourseJSON'](courseId='ENG101', name='English101')`

...or by optionally assigning the function to a variable and using it:

`CreateCourse = classes['CreateCourseJSON']`

`course = CreateCourse(courseId='ENG101', name='English101')`

The generated classes are **self-validating**--that is, you'll receive an error on instantiation if a required field is omitted, or if a wrong data type is assigned to a field, or if a value exceeds a field's maximum size...and so on, which should help reduce "400 Bad Request" errors. Each class also has a get_json() method that will return the properly-formatted JSON from objects, like so:

`course.get_json()`

`{"courseId": "ENG101", "name": "English101"}`

### Caveats

* Validation errors will return the entire schema for the object you're trying to validate, which gets pretty lengthy. I haven't found a way in warlock (the library I'm using to generate/validate the classes) to suppress that. Any tips or help would be greatly appreciated.
* There's also currently no way in the warlock library to create nested fields (e.g., availability in courses) directly. For the time being, you'll have to pass in nested values as their own dictionaries. For example:  

`avail={'availability':'Yes'}`

`course = CreateCourseJSON(courseId='ENG101', name='English 101', availability=avail)`

* Warlock will still validate nested fields, though. For instance, providing an invalid value for availability will throw an error.
