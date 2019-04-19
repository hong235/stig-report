## Code Dx Generic Operations Class
#
# This class is designed to perform a number of operations on a Code Dx server
# with minimal interaction from the user.  It is written to use Python3, and
# the "requests" package to perform all of the network operations.

import requests
import configparser
import json
import time
import sys

class CodeDx :
	## Constructor
	#
	# Each object points to a single server.  An operation that will always be
	# be preformed is to gather the project list from the server.  That is done
	# here automatically, and stored in an object dictionary.
	#
	# Network parameters are gathered from the init file (aka "config" file) and
	# stored as object parameters as well.
	#
	# Requests is used as a "session" to allow easy access to repeatedly used
	# headers.  Please note that all headers, and parameters are persistent and will
	# be repeated with each request.  Therefore, all uses should revert those two
	# fields back to the original values if possible.
	#
	# An upgrade to this class will be to allow any access to certificates from
	# "Let's Encrypt" servers to be used without ignoring the "self signed" certificate
	# warnings.  It would also show the user how to incorporate their own certs to
	# allow proper authentication when used.
	def __init__(self, ini) :
		
		# begin by building up the URL we will be using
		transport = ini.get('CodeDx', 'transport').lower()
		url = transport + '://' + ini.get('CodeDx', 'server')
		
		# omit the port if the server's transport matches the requested port.  Also,
		# the port number is optional, and may be omitted
		try :
			port = ini.get('CodeDx', 'port')
			if ( transport == 'http' ) and ( int(port) != 80 ) :
				url += ':' + str(port)
			else :
				if ( transport == 'https' ) and ( int(port) != 443 ) :
					url += ':' + str(port)
		
		# port number was not specified.  We will rely on the transport to select the
		# appropriate port.  This is not an error
		except :
			pass
		
		# append the Code Dx default location for API work and assign the entire
		# string to a reusable class scoped variable.
		self.url = url + '/codedx/api'
		self.urlx = url + '/codedx/x'	# for some experimental API calls
		print("|-- [Code Dx Constructor] using URL: \"%s\"" % self.url)
		
		# create a requests 'session' to store the data in general.  The URL is outside
		# of that scope
		self.session = requests.session()
		
		# add the default headers that are required
		headers = { 'accept' : 'application/json' }
		try :
			apikey = ini.get('CodeDx', 'api-key')
		except :
			print("|-- [Code Dx Constructor] ERROR: no API key specified in configuration file")
			raise ValueError("No API Key specified")
		
		headers['API-Key'] = apikey
		self.session.headers.update(headers)
		
		# add a proxy if necessary.  It will be used for the entire session
		# proxies = { 'http' : 'http://127.0.0.1:8090', 'https' : 'http://127.0.0.1:8090' }
		# self.session.proxies.update(proxies)
		
		# create a project dictionary to contain the Code Dx project ID.
		self.getProjectIds()
		
		# set up a storage location for getFileLines - trying to make this a little faster
		self.getFileStorage   = ''
		self.getFileStorageId = -1
	
	## getProjectIds
	#
	# Collect the project list from the API, and create a dictionary that has the list.
	# Since this list is created during the object's constructor, it should not be called
	# as the information is easily searchable in the generated dictionary.
	def getProjectIds(self) :
	
		# format the URL for the location we wish to accress
		url = self.url + '/projects'
		resp = self.session.get(url, verify = False)
		if resp.status_code != 200 :
			print("|-- [CDX getProjectIds] get projects responded [%d]" % resp.status_code)
			return {}
		
		# we got a good response.  De-Jsonize the response and return the dictionary
		list = resp.json()
		self.projectIds = {}
		for project in list['projects'] :
			self.projectIds[project['name']] = project['id']
			
	## createAnalysisPrep
	#
	# Create a new analysis prep against the desired project, and return the Analysis ID.
	# This will be needed to start the analysis when the file shipment is done.
	def createAnalysisPrep(self, project_id) :
	
		# begin by formatting the url we will use for this endpoint
		url = self.url + '/analysis-prep'
		payload = { 'projectId' : str(project_id) }
		resp = self.session.post(url, json = payload)
		if resp.status_code != 200 :
			print("|-- [CDX createAnalysisPrep] get prep returned [%d]" % resp.status_code)
			raise ValueError("createAnalysisPrep failed.")
			
		# got a good status back.  Grab the prep Id and return it
		prepId = resp.json()['prepId']
		print("|-- [CDX createAnalysisPrep] returning ID [%s]" % prepId)
		return prepId
	
	## queryJobStatus
	#
	# Return the status of the jobId
	def queryJobStatus(self, jobId) :
	
		# format the url we will make the request with
		url = self.url + '/jobs/' + str(jobId)
		resp = self.session.get(url)
		if resp.status_code != 200 :
			print("|-- [CDX queryJobStatus] queryJobStatus responded [%d]" % resp.status_code)
			raise ValueError("CDX jobId invalid for unknown reasons")
		
		# grab and return the job status
		jobStatus = resp.json()['status']
		return jobStatus
	
	## sendFileandWait
	#
	# Send the requested filename and wait until the job returns 'completed'
	def sendFileandWait(self, prepId, filename) :
	
		# format the url
		url = self.url + '/analysis-prep/' + prepId + '/upload'
		files = { 'file' : open(filename, 'rb') }
		self.session.params.update({ 'X-Client-Request-Id' : 'xyzzy22' })
		resp = self.session.post(url, files = files)
		self.session.params.update({ 'X-Client-Request-Id' : None })
		if resp.status_code != 202 :
			print("|-- [CDX sendFileandWait] responded [%d]" % resp.status_code)
			return False
		
		# got a good send.  Check the job status until it is done
		jobId = resp.json()['jobId']
		while True :
			status = self.queryJobStatus(jobId)
			if status == 'completed' :
				break
			time.sleep(1)
		
		# we're good!  File has been sent
		print("|-- [CDX sendFileandWait] sent \"%s\"" % filename)
		return True
		
	## runAnalysisandWait
	#
	# Run the prepared analysis and wait on the jobId until it finishes
	def runAnalysisandWait(self, analysis_id) :
	
		# format the url for this endpoint
		url = self.url + '/analysis-prep/' + analysis_id + '/analyze'
		resp = self.session.post(url)
		if resp.status_code != 202 :
			print("|-- [CDX runAnalysisandWait] responded [%d]" % resp.status_code)
			return False
			
		# grab the jobId for this analysis and wait until it is done.  We use 3 second
		# waits here as these usually take longer
		print("|-- [CDX runAnalysisandWait] analysis started")
		jobId = resp.json()['jobId']
		while True :
			status = self.queryJobStatus(jobId)
			if status == 'completed' :
				break
			time.sleep(3)
		
		# we're good!  Analysis is done
		print("|-- [CDX runAnalysisandWait] analysis completed.")
		return True
		
	## GetStandards
	#
	# Collect the standards available on this server
	def getStandards(self) :
	
		# format the url for this endpoint
		url = self.url + '/standards/filter-views'
		resp = self.session.get(url)
		if resp.status_code != 200 :
			print("|-- [CDX getStandards] responded [%d]" % resp.status_code)
			return []
		
		# grab the standards list and return it as an array of JSON data
		print("|-- [CDX getStandards] succeeded")
		return resp.json()
	
	## FindingsGroupedCount
	#
	# Collect findings by groups.  Currently used to collect the DISA STIG data
	#
	def findingsGroupedCount(self, project_id, filter) :
		
		# format the url for this endpoint
		url = self.url + '/projects/' + str(project_id) + '/findings/grouped-counts'
		resp = self.session.post(url, data = json.dumps(filter))
		if resp.status_code != 200 :
			print("|-- [CDX findingsGroupedCount] responded [%d]" % resp.status_code)
			return []
			
		# grab the list of findings counts and return the json
		print("|-- [CDX findingsGroupedCount] succeeded")
		return resp.json()
	
	## getCodeMetrics
	#
	# Collect part of the dashboard that returns code metrics.  We currently only capture
	# one day (the most recent).
	def getCodeMetrics(self, project_id) :
	
		# format the url for this endpoint
		url = self.urlx + '/dashboard/' + str(project_id)
		self.session.params.update({ 'includeChildProjects' : True })
		resp = self.session.post(url, data = json.dumps({ "codeMetrics" : { "latest" : '1' }}))
		
		# remove parameters that are for a specific call
		self.session.params.update({ 'includeChildProjects' : None })
		if resp.status_code != 200 :
			print("|-- [CDX getCodeMetrics] responded [%d]" % resp.status_code)
			return []
		
		# success.  Return the metrics
		print("|-- [CDX getCodeMetrics] succeeded")
		return resp.json()['codeMetrics']
		
	## findingTableData
	#
	# Collect the findings for the given filter and parameters
	def findingTableData(self, project_id, filter, params) :
		
		# format the url for this endpoint
		url = self.url + '/projects/' + str(project_id) + '/findings/table'
		self.session.params.update(params)
		resp = self.session.post(url, data = json.dumps(filter))
		if resp.status_code != 200 :
			print("|-- [CDX findingTableData] responded [%d]" % resp.status_code)
			return []
		
		# strip out the parameters we may have inserted
		for key, val in params.items() :
			val = None
		self.session.params.update(params)
		
		# return the successful list of data
		return resp.json()
	
	## getFileLines
	#
	# Collect the file information given the project ID, and file ID
	#
	# use this as an impromptu cache: self.getFileStorage
	#								  self.getFileStorageId
	#
	def getFileLines(self, project_id, location, count) :
		
		try :
			# format the url for this endpoint
			url = self.url + '/projects/' + str(project_id) + '/files/' + str(location['fileid'])
		except :
			return ' '

		# check to see if we already have this file in place.
		if self.getFileStorageId != location['fileid'] :
			resp = self.session.get(url)
			if resp.status_code != 200 :
				# print("|-- [CDX getFileLines] responded [" + str(resp.status_code) + "] for file ID [" + str(location['fileid']) + "]")
				return resp.text
			
			# file has been accessed.  Store it in the cache
			self.getFileStorage = resp.text.split('\n')
			self.getFileStorageId = location['fileid']
		
		# we have the file lines.  Trim them to the lines we need.
		loc = int(location['line'])
		count = int(count)
		lines = self.getFileStorage[loc - count : loc + count]
		
		# reformat lines to eliminate the array
		retval = ''
		for line in lines :
			retval += line
		
		return retval
		
		
	
	
	
	
	
		
		