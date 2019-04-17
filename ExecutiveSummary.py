#!/bin/python
# Collect and Return Executive Summary
#
import re
import json
import matplotlib.pyplot as plt

## Collect and Format Executive Summary
#
# 
def CollectExecutiveSummary(ini, cdx, project_id) :
	print("|- Begin collecting Executive Summary data")
	standards = cdx.getStandards()
	
	# we can now begin building our response.  Search the incoming server standards for
	# the most recent.  Record that string.
	stig_name = ''
	stig_version = ''
	countBy = ''
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
			if stig_version < version :
				stig_name = record['name']
				stig_version = version
				countBy = record['countBy']
	
	# report the computed version
	print("|- [CollectExecutiveSummary] Using " + stig_name)
	print("|- [CollectExecutiveSummary]   countBy = " + countBy)
	
	# we now have the data to create a filter for the DISA results.  This will generate the
	# numbers we need to format into our return data structure
	stig_filter = { 'filter': { '~status': [ 'fixed', 'mitigated', 'ignored', 'false-positive' ] } }
	stig_filter['countBy'] = countBy
	stig_data = cdx.findingsGroupedCount(project_id, stig_filter)
	
	# All of the data for the Executive Summary is ready.  Begin by grabbing the children
	# node.  We will report the findings
	print("|- STIG Total Count: " + str(stig_data[0]['count']))
	
	# collect and report individual STIG categories.  We set defaults before changing them
	stig_counts = { 'CAT I' : 0, 'CAT II' : 0, 'CAT III' : 0 }
	for cat in stig_data[0]['children'] :
		print("|- Counts for " + cat['name'] + " are " + str(cat['count']))
		stig_counts[cat['name']] = cat['count']
	
	# return the data necessary.
	stig_counts['version'] = stig_version
	return stig_counts, stig_data
	
## Format the Executive Summary Graphic
#
#
def FormatExecutiveGraphic(summary, graphic_filename) :
	
	# create the data sets we need
	objects = ( 'CAT I', 'CAT II', 'CAT III' )
	colors = ( 'red', 'orange', 'yellow' )
	y_pos = [ 0, 1, 2 ]
	values = [ summary['cat1Totals'], summary['cat2Totals'], summary['cat3Totals'] ]

	# form the output plot, and ship it to the correct file
	plt.bar(y_pos, values, align='center', alpha=1.0, color=colors)
	plt.ylabel('Findings')
	plt.xticks(y_pos, objects)
	plt.title('Findings by ASD STIG')
	plt.savefig(graphic_filename)
	
	