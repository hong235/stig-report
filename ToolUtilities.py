## Tool Description and other utilities
#

## Dictionary of tool names and descriptions
tool_table = { 'Fortify' 	     : 'Commercial static analysis tool',
			   'SpotBugs'	     : 'Open Source static analysis tool',
			   'AppScan Source'  : 'Commercial static analysis tool',
			   'Veracode'        : 'Commercial static analysis tool',
			   'Checkmarx'       : 'Commercial static analysis tool',
			   'PMD'             : 'Open Source static analysis tool',
			   'Nessus'          : 'Commercial network analysis tool',
			   'Burp Suite'      : 'Commercial dynamic analysis tool',
			   'ZAP'             : 'Open Source dynamic analysis tool',
			   'PHP_CodeSniffer' : 'Open Source static analysis tool',
			   'Retireljs'       : 'Open Source static analysis tool',
			   'ESLint'          : 'Open Source static analysis tool',
			   'Arachni'      	 : 'Commercial dynamic analysis tool'
			 }

## getDescription
#
# Return the tool description given the name.  Fails gracefully.
def getDescription(tool_name) :
	
	description = 'No tool description available'
	try :
		description = tool_table[tool_name]
	except :
		pass
	
	return description
	
	