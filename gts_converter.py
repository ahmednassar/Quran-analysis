# coding: utf-8

# In[10]:


#!/usr/bin/env python

#


# BEGIN_COPYRIGHT
#
# IBM Confidential
# OCO Source Materials
#
# com.ibm.watson.cnc:cnc-collection-service
# (C) Copyright IBM Corp. 2018 All Rights Reserved.
#
# The source code for this program is not published or otherwise
# divested of its trade secrets, irrespective of what has been
# deposited with the U.S. Copyright Office.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
#
# END_COPYRIGHT
#

'''
@auther Ahmed Nassar -- anassar@us.ibm.com
Create on May 1st, 2018
'''

''''
usage: gts_converter.py -i inputfile -o outputfile
Convert GTS (CSV) file formate into json format following the archeticture on
https://github.ibm.com/anassar/public-api-proposals/blob/master/v1-proposals/api-035-element-classification-feedback-event.md
Required arguments:
  -h, --help            show this help message and exit
  -i PATH, --input PATH  Path to a GTS (SCV) file
  -o PATH, --output PATH Path of the output json file
'''

import csv
import json
import uuid
from optparse import OptionParser
import sys
import argparse

document_names = {}

def read_csv(input_path):
    l = []
    with open(input_path) as fb:
        fbreader = csv.DictReader(fb, delimiter=',', dialect='excel', quotechar='"')
        for row in fbreader:
            if(row['type_disagree'] == 'Disagree' or row['categories_disagree'] == 'Disagree'):
                l.append(row)
    return l

def handleRow(row):
    do = {}
    document_id = str(uuid.uuid4())
    doc_name = row['document']
    if(doc_name in document_names):
        document_id = document_names.get(doc_name)
    else:
        document_names[doc_name] = document_id
    do['environment_id'] = str(uuid.uuid4())
    do['client_timestamp'] = ''
    do['collection_id'] = str(uuid.uuid4())
    do['document_id'] = document_id
    do['element_id'] = str(uuid.uuid4())
    do['sentence_text'] = row['sentence_text']
    do['comment'] = row['comments']
    fdo = {}
    #---------------actual data-------------------
    aco = {}
    tya = []
    tyo = {}
    tlabel = {}
    tlabel['nature'] = row['EC_nature']
    tlabel['party'] = row['EC_party']
    tyo['label'] = tlabel
    tyo['assurance'] = ''
    if(len(tlabel['party']) > 0 or len(tlabel['nature']) > 0):
        tya.append(tyo)
    cta = []
    cto = {}
    cto['label'] = row['EC_categories']
    cto['assurance'] = ''
    if(len(cto['label']) > 0):
        cta.append(cto)
    aco['types'] = tya
    aco['categories'] = cta
    fdo['original_labels'] = aco
    #---------------feedback - type ---------------------
    updated_labels = {}
    updated_types = []
    if(row['type_disagree'] == 'Disagree'):
        if(row['type_feedback'] != 'R'):
            if(len(row['type_feedback']) > 0):
                np = row['type_feedback'].split('–')
                if(len(np) == 2):
                    tyo = {}
                    tlabel = {}
                    tlabel['nature'] = np[0]
                    tlabel['party'] = np[1]
                    tyo['label'] = tlabel
                    if(len(tlabel['party']) > 0 or len(tlabel['nature']) > 0):
                        updated_types.append(tyo)
    else:
        tyo = {}
        tlabel = {}
        tlabel['nature'] = row['EC_nature']
        tlabel['party'] = row['EC_party']
        tyo['label'] = tlabel
        tyo['label'] = tlabel
        if(len(tlabel['party']) > 0 or len(tlabel['nature']) > 0):
            updated_types.append(tyo)
    updated_labels['types'] = updated_types
    fdo['updated_labels'] = updated_labels
    #-------------feedback - category ----------------
    updated_categories = []
    if(row['categories_disagree'] == 'Disagree'):
        cato = {}
        cato['label'] = row['categories_feedback']
        if(len(cato['label']) > 0):
            updated_categories.append(cato)
    else:
        cato = {}
        cato['label'] = row['EC_categories']
        if(len(cato['label']) > 0):
            updated_categories.append(cato)
    updated_labels['categories'] = updated_categories
    #-----------------------------------------------
    do['feedback_data'] = fdo
    return do
def main():
    parser = argparse.ArgumentParser(description='Convert local pdf files to html')
    parser.add_argument('-i', '--input_path', type=str, help='Input file path to a GTS (SCV) file',  required=True)
    parser.add_argument('-o', '--output_path', type=str, help='Output path of the output json file',  required=True)

    args = parser.parse_args()
    rows = read_csv(args.input_path)
    jl = []
    for row in rows:
        jl.append(handleRow(row))
    with open(args.output_path,"w") as f:
        json.dump(jl, f, indent=4)

main()
print("documents no. is", len(document_names))