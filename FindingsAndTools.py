## Collect Findings, and Tools data
#
#
import re
import json
import sys

## Helper routine to fill in structure data
#
def fillData(stack, cat) :
	while True :
		# get the item to process
		try :
			item = stack.pop()
		except :
			break	# all done!  Pop returned an index error
		
		if 'children' in item :
			# if there are children, put them on the stack and continue.
			stack.extend(item['children'])
		else :
			# no children, process the information
			name = item['name'].split(' ')[0]
			tmp = { }
			tmp['name'] = name
			tmp['filter_id'] = item['id']
			tmp['description'] = item['name'][ len(name) + 1 :]
			tmp['fcount'] = item['count']
			cat[name] = tmp

	
## Fully populate the 'stig', and 'cat' 1/2/3 areas fully
#
# The only exception to full population is in the 'cat' sections.  The 'acount' or
# actual counts come later when examining the findings
#
def CollectFiltersAndStigData(stig_data, cat1, cat2, cat3) :
	# we use a simple stack operation.  This assumes that there are no duplicates in the
	# incoming data stream.  We collect all of the children at each level, and put their
	# objects on the stack.  If the object has no children, we record the data it
	# contains.  Otherwise, the children are placed on the stack for processing.
	stack = []
	try :
		stack.extend(stig_data[0]['children'][0]['children']) # location of CAT I data
	except :
		print("|-- [FindingsAndTools.get.CollectFiltersAndStigData] no CAT I data")
		return
		
	fillData(stack, cat1)
	
	stack = []
	try :
		stack.extend(stig_data[0]['children'][1]['children']) # location of CAT I data
	except :
		print("|-- [FindingsAndTools.get.CollectFiltersAndStigData] no CAT II data")
		return
		
	fillData(stack, cat2)
	
	stack = []
	try :
		stack.extend(stig_data[0]['children'][2]['children']) # location of CAT I data
	except :
		print("|-- [FindingsAndTools.get.CollectFiltersAndStigData] no CAT III data")
		return
		
	fillData(stack, cat3)

## processFindings
#
# Process reads for a list of findings for each of the STIGS.  They are grouped by CAT
# level only.  This may change in the future
def processFindings(in_cat, cdx, project_id) :
		
	# begin by looping through all of the 'cat' name dictionaries.  We use each entry to
	# gather data from the Code Dx server
	total = 0
	for key, cat in in_cat.items() :
		# use the filter_id item to construct a query filter that will be used for this
		# item's results
		filter = { 'filter' : { '~status' : [ 'ignored', 'false-positive', 'mitigated', 'gone', 'fixed'] }}
		filter['filter']['standard'] = cat['filter_id']
		filter['sort'] = { 'by' : 'id', 'direction' : 'ascending' }
		filter['pagination'] = { 'page' : 1, 'perPage' : 2500 }
		
		# gather the information for the findings for this STIG from Code Dx
		params = { 'expand' : 'results.descriptor,results.metadata' }
		findings = cdx.findingTableData(project_id, filter, params)
		
		# now that we have fingings, lets format the information into this 'cat'
		cat['findings'] = []
		for finding in findings :
			# create a dictionary to collect the findings into
			list = {}
			list['id']    = finding['id']
			list['error'] = finding['descriptor']['name']
			try :
				list['location'] = { 'path' : finding['location']['path']['path'],
									 'file' : finding['location']['path']['shortName'],
									 'line' : finding['location']['lines']['start']
								   }
			except :
				list['location'] = { 'path' : '', 'file' : '', 'line' : '' }
					
			list['tools'] = [ ]
			for result in finding['results'] :
				tool_item = { }
				tool_item['name'] = result['tool']
				
				# metadata may not exist.  We try to put it here anyway.  If no metadata,
				# we simply insert a blank dictionary.
				try :
					tool_item['metadata'] = result['metadata']
				except :
					tool_item['metadata'] = { }
					
				list['tools'].append(tool_item)
					
			# add all of this data to the incoming 'cat'
			cat['findings'].append(list)
		
		# after all of the findings have been added, collect the total
		total += len(cat['findings'])
		
		print("|-- [processFindings] " + cat['name'] + " - records = " + str(len(cat['findings'])) + " and fcount = " + str(cat['fcount']))
	
	# return the total number of items to the caller
	return total

## processToolCounts
#
# Using the incoming structure, we count the tools into the tools dictionary.
#
def processToolCounts(in_cat, tools) :

	# loop through all of the names from the in_cat structure and create counters for tools
	# that exist
	for key, cat in in_cat.items() :
		# look into the 'findings' field to grab the tool names
		for finding in cat['findings'] :
			# now loop through the tools section
			for t in finding['tools'] :
				# look for the name in the incoming 'tools' dictionary.  If it does not exist
				# we simply create it
				try :
					tools[t['name']]['count'] += 1
				except :
					tools[t['name']] = { }
					tools[t['name']]['count'] = 1
	
#	print("\n\n", tools, "\n\n")
	
	
## Main Entry Point 'get'
#
#	
def get(ini, cdx, project_id) :
	
	# this will get complicated.  Hence a new file in the list!
	# Here is the new data structure we will be using to return
	#
	# {
	#	'stig' : {
	#				'name' : name of the stig
	#               'version' : version number as string (i.e. '4.3')
	#               'countBy' : count by filter string
	#            }
	#   'cat1' : { 
	#               'name' : {
	#                           'name'        : name of the filter as STIG (i.e. 'APSC-DV-000460')
	#                           'filter_id'   : filter id for later (i.e. 'standard-node:3287')
	#                           'description' : description of the STIG
	#                           'fcount'      : count from the origin of the filter. Used for verification
	#                           'findings'    : [
	#                                              {
	#                                                 'id'       : Code Dx ID of the finding
	#                                                 'location' : {
	#                                                                 'path' : path to the file
	#                                                                 'file' : filename of the location
	#                                                                 'line' : line number of the location
	#                                                              }
	#                                                 'error'    : Name of the rule violated
	#                                                 'tools'    : [ ] List of dictionary of tool 'name', 'metadata'
	#                                              }
	#                                           ]
	#                        }
	#            }
	#   'cat1Totals' : total finding counts.  May contain duplicates.
	#
	#   'cat2' : { 
	#               ... see 'cat1'
	#            }
	#   'cat2Totals' : total finding counts.  May contain duplicates.
	#
	#   'cat3' : { 
	#               ... see 'cat1'
	#            }
	#   'cat3Totals' : total finding counts.  May contain duplicates.
	#   
	#   'tools' : {
	#                'name' : {				: name of the tool is the key to this field
	#                            'count'	: number of findings calculated for this tool
	#             }
	# }
	#
	retval = { 'stig' : {} }
	
	# begin by obtaining the standard we will use for later reference
	standards = cdx.getStandards()
	
	# Generate the information for looking at findings through the lens of STIGs
	# This section of the database is used to collect the countBy field to allow
	# creation of a GroupedFilter later.  We will be using the strings for reporting
	stig = retval['stig']
	stig['name'] = ''
	stig['version'] = ''
	stig['countBy'] = ''
	for record in standards :
		if 'DISA STIG' in record['name'] :
			
			# grab the numeric version from the end of the name, and store it as the
			# version.  Then check to see if it is more or less than the current.
			# We use regular expressions to grab the number.  Since we know the string
			# will only have one (and it must be there), we can simply grab the first
			# elment of the list
			version = re.findall('[0-9]+\.[0-9]+', record['name'])[0]
			print("|- [CollectExecutiveSummary] Found DISA STIG version " + version)
			
			# compare the version we collected to the stored version.
			if stig['version'] < version :
				stig['name'] = record['name']
				stig['version'] = version
				stig['countBy'] = record['countBy']

	print("|- [FindingsAndTools.get] -- collected STIG version and filtering information")
	
	# Collect the grouped counts.  I've not found this to be terribly reliable.  So we simply
	# access the violation filters for later queries.
	stig_filter = { 'filter': { '~status': [ 'fixed', 'mitigated', 'ignored', 'false-positive' ] } }
	stig_filter['countBy'] = stig['countBy']
	stig_data = cdx.findingsGroupedCount(project_id, stig_filter)
	
	# here is where we collect information about filtering for each of the violated STIGs.  We
	# are filling out the 'cat' 1/2/3 section of the data structure
	retval['cat1'] = {  }
	retval['cat2'] = {  }
	retval['cat3'] = {  }
	CollectFiltersAndStigData(stig_data, retval['cat1'], retval['cat2'], retval['cat3'])
	
	# Now the real query work begins.  We loop through all of the category's findings and
	# gather details for each of the cat levels.  This will populate the information in
	# the 'findings' portion of each cat.
	for name in [ 'cat1', 'cat2', 'cat3' ] :
		print("|- [FindingsAndTools.get] -- " + name.upper() + " Finding collection - length = " + str(len(retval[name])))
		totals = processFindings(retval[name], cdx, project_id)
		print("|- [FindingsAndTools.get] -- " + name.upper() + " Totals = " + str(totals))
		
		# adjust the name to store the totals for this CAT level
		name += 'Totals'
		retval[name] = totals
	
	# Postprocess all of the data to collect the tool counts.  We simply leaf through all three
	# cats in the data structure, and count into the 'tools' section.  This will tell us the
	# numbers.  A record for a tool is only created when the tool name is encountered.
	retval['tools'] = { }
	for name in [ 'cat1', 'cat2', 'cat3' ] :
		processToolCounts(retval[name], retval['tools'])

	# return the data we have collected
	return retval
	
	
	