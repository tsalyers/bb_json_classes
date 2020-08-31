import urllib.request
from urllib.error import HTTPError
import json
import jmespath
import warlock


# Helper function for loading the Swagger API specs from Blackboard. 
# TODO: Error handling for invalid versions, connection errors, 404s, etc.
def load_swagger(version=None):
	base_url='https://developer.blackboard.com/portal/docs/apis/learn-swagger'
	# If we haven't had a version specified, just grab the latest, which is the default.
	# Otherwise, given a version like '3800.17.0', grab the Swagger JSON for that version.\
	if version is None:
		swagger_url = base_url + '.json'
	else:
		swagger_url = base_url + '-' + version + '.json'

	# Grab our Swagger JSON from Blackboard. 
	with urllib.request.urlopen(swagger_url) as url:
		swagger_data=json.loads(url.read().decode())
		return swagger_data


def get_json_classes(version=None):
	# This'll hold the classes we generate from the JSON. 
	bb_jsonclasses = {}

	# Small convenience method for the classes we build to make things a little neater.
	# You could json.dumps() everything, but that's kind of ugly, so we'll hide it.
	def get_json(self):
		return json.dumps(self)

	# Grab our Swagger JSON and iterate over the available paths. 
	data = load_swagger(version)
	paths=jmespath.search('paths',data)
	for path in paths.keys():	
		# NB: Need to quote the path; the slashes are jmespath special characters and need to be escaped.
		summary = jmespath.search('paths."' + path + '".post.summary',data)
		if summary is not None:
			# Got a path with a POST method available. Now check for deprecation:
			isDeprecated = jmespath.search('paths."' + path + '".post.deprecated',data)
			
			if isDeprecated:
				# Deprecated call. Ignore it.
				pass
			else:
				# Get the fields and their required status for the current path/call.
				parameters=jmespath.search('paths."' + path + '".post.parameters[0].schema.properties', data)
				required=jmespath.search('paths."' + path + '".post.parameters[0].schema.required', data)
				
				# Really terrible hacky bit. This exists because we're using the summary field to name classes, 
				# but both system and course announcements are called "Create Announcement" in their summaries.
				# Need to get Blackboard to change one summary or the other.
				if path=='/learn/api/public/v1/announcements':
					summary = 'Create System Announcement'
				elif path=='/learn/api/public/v1/courses/{courseId}/announcements':
					summary = 'Create Course Announcement'

				# Name the current class.
				# For now, just remove whitespace and tack "JSON" on the end.
				classname = summary.replace(" ","") + 'JSON'

				# The warlock library needs to have a top-level "type":"object" setting, and then parameters 
				# need to be enclosed in a "properties" heading after that. 
				#
				# Bonus: including the "required" field values and setting additionalProperties 
				# to False means any missing/erroneous fields will make objects fail validation 
				# immediately upon creation. This should cut down on 400 Bad Request errors on submission.
				#
				currentschema={"name":classname, "type":"object", "properties":parameters, "required": required, "additionalProperties":False}

				# Generate our class, add our getJSON method to it, and store it in our class dictionary:
				currentclass=warlock.model_factory(currentschema)
				currentclass.get_json = get_json
				bb_jsonclasses[classname] = currentclass
			
	return bb_jsonclasses



# Let's do a test construction of a CreateCourseJSON object. 
# NB: Warlock doesn't currently handle nested properties, so if you need to handle, say, availability
# in a course, you'll need to pass in a dictionary for the relevant property. For example:
# 
# avail={'availability':'Yes'}
# mycourse = CreateCourseJSON(courseId="ENG200", name="English 200", availability=avail)
'''
jsonclasses = get_json_classes()
print("Current JSON classes: " + str(jsonclasses.keys()) )
CreateCourseJSON = jsonclasses['CreateCourseJSON']
testcourse = CreateCourseJSON(courseId="ENG101", name="English 101", externalId="ENG101",description="Test description")
print(testcourse.getJSON())
'''
