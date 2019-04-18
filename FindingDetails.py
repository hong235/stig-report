#!/usr/bin/python
##
#
#
import sys
import xml.etree.ElementTree as ET

## Process details for STIG finding
#
#
def processTableData(parent, find) :

	# create the top table line
	block_attr = { 'font-size' : '8',
				   'border-width' : 'thin',
				   'text-align' : 'center',
				   'table-layout' : 'fixed',
				   'border-collapse' : 'collapse' }
				   
	cell_attr = { 'border-width' : 'thin', 'border-style' : 'solid' }
				   
	# create the header line
	ta = ET.SubElement(parent, 'fo:table', block_attr)
	ET.SubElement(ta, 'fo:table-column', { 'column-width' : '10%' })
	ET.SubElement(ta, 'fo:table-column', { 'column-width' : '45%' })
	ET.SubElement(ta, 'fo:table-column', { 'column-width' : '45%' })
	tb = ET.SubElement(ta, 'fo:table-body')
	
	# Now the actual first table begins (the headers)
	tr = ET.SubElement(tb, 'fo:table-row', { 'background-color' : 'LightSkyBlue' })
	tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
	ET.SubElement(tc, 'fo:block').text = 'ID'
	tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
	ET.SubElement(tc, 'fo:block').text = 'Location'
	tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
	ET.SubElement(tc, 'fo:block').text = 'Error Type'
	
	# Add finding data to the next row
	tr = ET.SubElement(tb, 'fo:table-row')
	tc = ET.SubElement(tr, 'fo:table-cell', { 'border-width' : 'thin', 'border-style' : 'solid' })
	ET.SubElement(tc, 'fo:block').text = str(find['id'])
	tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
	ET.SubElement(tc, 'fo:block').text = find['location']['path'] + ':' + str(find['location']['line'])
	tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
	ET.SubElement(tc, 'fo:block').text = find['error']
	
	# Begin the table for the tools loop
	ta = ET.SubElement(parent, 'fo:table', block_attr)
	ET.SubElement(ta, 'fo:table-column', { 'column-width' : '25%' })
	ET.SubElement(ta, 'fo:table-column', { 'column-width' : '75%' })
	tb = ET.SubElement(ta, 'fo:table-body')
	
	# add the header
	tr = ET.SubElement(tb, 'fo:table-row', { 'background-color' : 'LightSkyBlue' })
	tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
	ET.SubElement(tc, 'fo:block').text = 'Detected by'
	tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
	ET.SubElement(tc, 'fo:block').text = 'Vendor ID (when available)'
	
	# loop in the tools
	for tool in find['tools'] :
		tr = ET.SubElement(tb, 'fo:table-row')
		tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
		ET.SubElement(tc, 'fo:block').text = tool['name']		
		tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
		md_key = ''
		md_val = ''
		for md_key, md_val in tool['metadata'].items() :
			pass
		ET.SubElement(tc, 'fo:block').text = str(md_key) + " : " + str(md_val)
		
	# Begin the table for the example code
	block_attr['space-after'] = '15pt'
	ta = ET.SubElement(parent, 'fo:table', block_attr)
	ET.SubElement(ta, 'fo:table-column', { 'column-width' : '100%' })
	tb = ET.SubElement(ta, 'fo:table-body')
	
	# add the header
	tr = ET.SubElement(tb, 'fo:table-row', { 'background-color' : 'LightSkyBlue' })
	tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
	ET.SubElement(tc, 'fo:block').text = 'Example Code'
	
	tr = ET.SubElement(tb, 'fo:table-row')
	tc = ET.SubElement(tr, 'fo:table-cell', cell_attr)
	code_attr = { 'linefeed-treatment' : 'preserve',
				  'width' : '95%',
				  'wrap-option' : 'wrap',
				  'linefeed-treatment' : 'preserve',
				  'white-space' : 'pre',
				  'white-space-collapse' : 'false',
				  'font-family' : 'monospace',
				  'font-size' : '8',
				  'text-align' : 'left',
				  'space-after' : '15pt' }
	ET.SubElement(tc, 'fo:block', code_attr).text = find['code']
	
	
	
## Process each STIG item
#
# Format the header for each STIG, then loop in the findings details
def processStig(parent, cat_name, cat) :
	
	# loop over all of the STIGs in this CAT
	for stig_name, stig in cat.items() :
	
		# process the header that looks nice to describe the current STIG.  The block
		# has so many elements, I split it out for easy maintenance
		block_attr = { 'id'					 : stig_name,
					   'space-before'		 : '15pt',
					   'font-size'			 : '12pt',
					   'font-family'		 : 'sans-serif',
					   'space-after'		 : '15pt',
					   'color'				 : 'white',
					   'background-color'	 : 'LightSkyBlue',
					   'text-align'      	 : 'justify',
					   'padding-top'		 : '3pt' }
		bl = ET.SubElement(parent, 'fo:block', block_attr)
		bl.text = "STIG " + stig_name + " - " + cat_name + " " + stig['description']
		
		# now loop and process all of the actual findings
		for find in stig['findings'] :
			processTableData(parent, find)
					   
	
### Format Finding Details
#
# This formats the individual finding details.  We begin at the STIG level, and 
# loop through each STIG, followed by looping through all of the findings that
# are associated with it.  Formatting the cells as we go.
#
def details(parms) :

	# begin operation by eliminating the 'CodeDx' tag from the XML
	parent = parms['parent']
	parent.remove(parms['child'])
	
	# Start the process by looping across all of the cats.  There are three.
	# actual formatting is performed in the subroutine.
	cat_name = { 'cat1' : 'CAT I', 'cat2' : 'CAT II', 'cat3' : 'CAT III' }
	for cat in [ 'cat1', 'cat2', 'cat3' ] :
		processStig(parent, cat_name[cat], parms['summary'][cat])
