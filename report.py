#!/usr/bin/python
## Report Writer CodeDx
#
import configparser
import argparse
import codedx
import ExecutiveSummary as es
import ReportLanguage as rl
import FindingsAndTools
import FindingDetails as fd
import ToolUtilities
import xml.etree.ElementTree as ET
import datetime
import re

## Table of Contents DISA STIG Version
#
def tocDisaStigVersion(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])
	
	# format the output
	elem = ET.SubElement(parent, 'fo:block')
	elem.attrib['text-align'] = "start"
	elem.attrib['text-align-last'] = "justify"
	elem.attrib['font-size'] = "11pt"
	elem.text = "Finding Counts by ASD STIG Version " + parms['summary']['stig']['version']
	
	# add the dots after the element
	leader = ET.SubElement(elem, 'fo:leader')
	leader.attrib['leader-pattern'] = "dots"
	leader.attrib['leader-alignment'] = "reference-area"

## AddReportDate
#
# Add the date to the object for the Executive Summary "Project Date:"
def reportDate(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])
	now = datetime.datetime.now()
	
	# format the output
	elem = ET.SubElement(parent, 'fo:block')
	elem.text = 'Project Date: ' + now.strftime("%d-%b-%Y %Z")

## projectName
#
# Add a project name set of records
def projectName(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])
	
	# format the output
	elem = ET.SubElement(parent, 'fo:block')
	elem.text = 'Project Name: ' + parms['project']
	

## disaStigVersion
#
# Add records for the version of DISA ASD STIG we are using
def disaStigVersion(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])
	
	# format the output
	elem = ET.SubElement(parent, 'fo:block')
	elem.text = "DISA ASD STIG Version " + parms['summary']['stig']['version']

## Rewrite CAT finding counts in table
#
# 
def catCells(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])
	
	# format the cells for the counts in the Executive Summary table
	cell = ET.SubElement(parent, 'fo:table-cell', { 'border-width': 'thin', 'border-style': 'solid' })
	cellb = ET.SubElement(cell, 'fo:block')
	cellb.text = str(parms['summary']['cat1Totals'])
	cell = ET.SubElement(parent, 'fo:table-cell', { 'border-width': 'thin', 'border-style': 'solid' })
	cellb = ET.SubElement(cell, 'fo:block')
	cellb.text = str(parms['summary']['cat2Totals'])
	cell = ET.SubElement(parent, 'fo:table-cell', { 'border-width': 'thin', 'border-style': 'solid' })
	cellb = ET.SubElement(cell, 'fo:block')
	cellb.text = str(parms['summary']['cat3Totals'])

## findingCountsByStig
#
# replace the title heading on the destination page
def findingCountsByStig(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])

	# replace the title.  Remember this if the color of the headings is changed
	block = ET.SubElement(parent, 'fo:block')
	block.attrib['id'] = "finding-counts-by-stig"
	block.attrib['space-before'] = "15pt"
	block.attrib['font-size'] = "24pt"
	block.attrib['font-family'] = "sans-serif"
	block.attrib['space-after.optimum'] = "15pt"
	block.attrib['color'] = "white"
	block.attrib['background-color'] = "LightSkyBlue"
	block.attrib['text-align'] = "left"
	block.attrib['padding-top'] = "3pt"
	block.attrib['break-before'] = "page"
	
	block.text = "Finding Counts by ASD STIG Version " + parms['summary']['stig']['version']

####################
# CAT I/II/III Stig Counts
####################

## Cat I Format Table Entry
#
#
def formatCatTableEntry(xml, stig) :	
	# format the table row in XML
	row = ET.SubElement(xml, "fo:table-row")
	cell = ET.SubElement(row, "fo:table-cell", { 'border-width' : 'thin', 'border-style' : 'solid' })
	block = ET.SubElement(cell, "fo:block")
	block.text = stig['name']
	cell = ET.SubElement(row, "fo:table-cell", { 'border-width' : 'thin', 'border-style' : 'solid', 'text-align' : 'left', 'padding-left' : '5pt' })
	block = ET.SubElement(cell, "fo:block")
	block.text = stig['description']
	cell = ET.SubElement(row, "fo:table-cell", { 'border-width' : 'thin', 'border-style' : 'solid' })
	block = ET.SubElement(cell, "fo:block")
	block.text = str(len(stig['findings']))
	
	if len(stig['findings']) > 0 :
		cell = ET.SubElement(row, "fo:table-cell", { 'border-width' : 'thin', 'border-style' : 'solid', 'font-family' : 'Courier', 'color' : 'red' })
		block = ET.SubElement(cell, "fo:block")
		block.text = 'FAIL'
	else :
		cell = ET.SubElement(row, "fo:table-cell", { 'border-width' : 'thin', 'border-style' : 'solid', 'font-family' : 'Courier', 'color' : 'green' })
		block = ET.SubElement(cell, "fo:block")
		block.text = 'PASS'

## Add entry on STIG array
#
# This allows for deduplication (if it exists), and to order the stig records as desired.
# We are sorting on the STIG ID
def makeEntry(xml, description, count) :
	# capture the STIG ID.  It is what we will use for the returned STIG array of
	# dictionaries
	id = description.split(' ')[0]
	desc = description[len(id) + 1:]
	return { 'parent' : xml, 'id' : id, 'desc' : desc, 'count' : str(count) }

	
## Format CAT I Stig counts into table
#
#
def cat1StigCounts(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])
					
	# loop through the entries and write table records
	for key, item in sorted(parms['summary']['cat1'].items()) :
		formatCatTableEntry(parent, item)

## Format CAT II Stig counts into table
#
#
def cat2StigCounts(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])

	# loop through the entries and write table records
	for key, item in sorted(parms['summary']['cat2'].items()) :
		formatCatTableEntry(parent, item)

## Format CAT III Stig counts into table
#
#
def cat3StigCounts(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])

	# loop through the entries and write table records
	for key, item in sorted(parms['summary']['cat3'].items()) :
		formatCatTableEntry(parent, item)

####################
# CAT I/II/III Stig Counts End
####################

## Tool Findings
#
#
def toolFindings(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])
	
	# loop through the tools and set the findings.  Ignore the description for now
	for key, item in parms['summary']['tools'].items() :
		tr = ET.SubElement(parent, 'fo:table-row')
		tc = ET.SubElement(tr, 'fo:table-cell', { 'border-style' : 'solid', 'text-align' : 'center' })
		bl = ET.SubElement(tc, 'fo:block')
		bl.text = str(item['count'])
		
		tc = ET.SubElement(tr, 'fo:table-cell', { 'border-style' : 'solid', 'text-align' : 'center' })
		bl = ET.SubElement(tc, 'fo:block')
		bl.text = key

		tc = ET.SubElement(tr, 'fo:table-cell', { 'border-style' : 'solid', 'text-align' : 'left', 'padding-left' : '5pt' })
		bl = ET.SubElement(tc, 'fo:block')
		bl.text = ToolUtilities.getDescription(key)

## Tool Total Findings
#
#
def toolTotalFindings(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])
	
	blk = ET.SubElement(parent, 'fo:block')
	blk.text = str(parms['summary']['toolsFindings'])

## Table of Contents Details
#
# 
def tocDetails(parms) :
	parent = parms['parent']
	parent.remove(parms['child'])
	
	# CAT I keys
	for key, item in parms['summary']['cat1'].items() :
		tr = ET.SubElement(parent, 'fo:table-row')
		tc = ET.SubElement(tr, 'fo:table-cell')
		bl = ET.SubElement(tc, 'fo:block', { 'text-align' : 'start', 'font-size' : '9pt', 'text-align-last' : 'justify', 'margin-left' : '05%' })
		bl.text = key
		ET.SubElement(bl, 'fo:leader', { 'leader-pattern' : 'dots', 'leader-alignment' : 'reference-area' })
		
		tc = ET.SubElement(tr, 'fo:table-cell')
		bl = ET.SubElement(tc, 'fo:block', { 'text-align' : 'end' })
		
		link = ET.SubElement(bl, 'fo:basic-link', { 'internal-destination' : key })
		ET.SubElement(link, 'fo:page-number-citation', { 'ref-id' : key })
	
	# CAT II keys
	for key, item in parms['summary']['cat2'].items() :
		tr = ET.SubElement(parent, 'fo:table-row')
		tc = ET.SubElement(tr, 'fo:table-cell')
		bl = ET.SubElement(tc, 'fo:block', { 'text-align' : 'start', 'font-size' : '9pt', 'text-align-last' : 'justify', 'margin-left' : '05%' })
		bl.text = key
		ET.SubElement(bl, 'fo:leader', { 'leader-pattern' : 'dots', 'leader-alignment' : 'reference-area' })
		
		tc = ET.SubElement(tr, 'fo:table-cell')
		bl = ET.SubElement(tc, 'fo:block', { 'text-align' : 'end' })
		
		link = ET.SubElement(bl, 'fo:basic-link', { 'internal-destination' : key })
		ET.SubElement(link, 'fo:page-number-citation', { 'ref-id' : key })
	
	# CAT III keys
	for key, item in parms['summary']['cat3'].items() :
		tr = ET.SubElement(parent, 'fo:table-row')
		tc = ET.SubElement(tr, 'fo:table-cell')
		bl = ET.SubElement(tc, 'fo:block', { 'text-align' : 'start', 'font-size' : '9pt', 'text-align-last' : 'justify', 'margin-left' : '05%' })
		bl.text = key
		ET.SubElement(bl, 'fo:leader', { 'leader-pattern' : 'dots', 'leader-alignment' : 'reference-area' })
		
		tc = ET.SubElement(tr, 'fo:table-cell')
		bl = ET.SubElement(tc, 'fo:block', { 'text-align' : 'end' })
		
		link = ET.SubElement(bl, 'fo:basic-link', { 'internal-destination' : key })
		ET.SubElement(link, 'fo:page-number-citation', { 'ref-id' : key })
	
## Main Entry Point
#
def main(args) :
	
	# begin by grabbing our configuration, and parse it
	print(":----------")
	print("|- reading configuration")
	ini = configparser.ConfigParser()
	ini.read(args.config)
	
	# create a Code Dx object
	cdx = codedx.CodeDx(ini)
	project_name = ini.get('CodeDx', 'project')
	project_id = cdx.projectIds[project_name]
	print("|- Project " + project_name + " has ID", project_id)
	
	# begin the report by ingesting the information we need to create the report itself.
	# It will be contained in a data structure designed to hold all of the relevant
	# elements.  Let's begin.  First, we gather counts such that we can create the data
	# for the 'Executive Summary'
	#   Format: [
	#           ]
	#
	# Note that the data is duplicated for each of the STIG levels.  This is so small, I
	# decided to do it the easy way.
	#summary_data, stig_counts = es.CollectExecutiveSummary(ini, cdx, project_id)
	
	# perform the queries to generate additional data for findings, and tools
	summary_data = FindingsAndTools.get(ini, cdx, project_id, ini.get('Report', 'code_detail'))
	
	# now that we have the data, form up the graphics
	es.FormatExecutiveGraphic(summary_data, ini.get('Report', 'graphic_filename'))
	
	# This is a call table used to collect the CodeDx elements "content" attribute into.
	# When the attribute is determined, a subroutine is called to create the appropriate
	# records to be placed into our tree.  This is a simple dictionary.
	CodeDxContents = { 'TOCstigVersion'      : tocDisaStigVersion,
					   'ReportDate'          : reportDate,
					   'ProjectName'         : projectName,
					   'DisaStigVersion'     : disaStigVersion,
					   'CatCells'            : catCells,
					   'FindingCountsByStig' : findingCountsByStig,
					   'CatIStigCounts'      : cat1StigCounts,
					   'CatIIStigCounts'     : cat2StigCounts,
					   'CatIIIStigCounts'    : cat3StigCounts,
					   'languages'           : rl.languageCells,
					   'ToolFindings'        : toolFindings,
					   'ToolTotalFindings'   : toolTotalFindings,
					   'ToCDetails'          : tocDetails,
					   'FormatFindingDetail' : fd.details
					 }
	
	# load our XML template into memory for modification
	template_file = ini.get("Report", "template")
	print("|- Loading template \"" + template_file + "\"")
	
	# load up the "fo:" namespace before loading in the template.  This prevents the tags
	# from being rewritten to "ns0"
	ET.register_namespace('fo', "http://www.w3.org/1999/XSL/Format")
	tree = ET.parse(template_file)
	root = tree.getroot()
	
	# Now it is successfully loaded into memory.  This is a little weird... we cannot get
	# the parent of a node.  So we have to get the parents (using XPath ".//CodeDx/..") and
	# search for the element we need to replace... the CodeDx element.  But now we have
	# the parent
	print("|- Loaded report template")
	code_dx_parent_tags = root.findall(".//CodeDx/..")

	# A consistent call format is used.  The input dictionary is call specific and 
	# contains elements that are required.
	call_dict = { 'project'   : project_name,
				  'summary'   : summary_data,
				  'cdx'       : cdx,
				  'proj_id'   : project_id
				}
	
	# look at each of the parents and find the "CodeDx" tag we need to replace
	for parent_code_dx in code_dx_parent_tags :
		
		# save the parent for our call in our generic parameters list
		call_dict['parent'] = parent_code_dx
		
		# find all of the CodeDx elements and return them
		code_dx_list = parent_code_dx.findall(".//CodeDx")
		
		for code_dx in code_dx_list :
			# call the appropriate routine from our CodeDxContents subroutine to generate
			# the records we need directly into the parent XML
			call_dict['child'] = code_dx
			CodeDxContents[code_dx.attrib['content']](call_dict)
	
	# write the resultant XML file into our output
	tree.write(ini.get('Report', 'fo_output'), xml_declaration=True, encoding='utf-8', method='xml')
	print("|- Writing output FO file \"" + ini.get('Report', 'fo_output') + "\"")

	
## Environment Entry Point
#
desc = 'Collect information to generate customer specialized report.\n'
parser = argparse.ArgumentParser(description=desc)
parser.add_argument("--config",   "-c", required=True, help="Input configuration file")
args = parser.parse_args()

if __name__ == "__main__" :
	try :
		main(args)
	except ValueError as e :
		pass
		
	print(":---------- Done.")
