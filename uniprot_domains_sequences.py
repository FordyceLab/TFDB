import requests
import sys
import json
import re
from socket import timeout
from urllib.error import URLError
from bs4 import BeautifulSoup as soup
from math import ceil
#functions to get various information about proteins using their uniprot ids
#and the proteins API:https://doi.org/10.1093/nar/gkx237

def get_domains(accession, fields, domain_names):
    '''This function take in a uniprot accession id as a string, a list of
    fields (strings) in the json to search, and a domain name compiled regex
    string to compare, and outputs a list of dictionaries where each dictionary
    is a dna binding domain with the keys uniprot ids, dna binding domain
    description, start, and stop.'''

    domain_output = []
    domains = []
    query_start = 'http://www.ebi.ac.uk/proteins/api/features/'

    #searching by the feature types
    feature_type_query = '?types='+','.join(fields)
    query = query_start+accession+feature_type_query
    #getting the requests as a json
    r = requests.get(query).json()
    try:

        for feature in r['features']:
            dbd_type, start, stop = None, None, None

            #if the feature type is a zinc finger or a dna binding domain,
            #there's no need to check the fields to see if they match the dbd
            #regex.
            if feature['type']=='ZN_FING' or feature['type'] == 'DNA_BIND':
                dbd_type, start, stop = feature['description'], \
                feature['begin'], feature['end']
                if start:
                    domains.append((dbd_type, start, stop))

            #since there are non-dna binding domains in the domains and regions
            #fields, the regex needs to be used to see only get the dna binding
            #domains
            else:
                if re.search(domain_names, feature['description']):
                    dbd_type, start, stop = feature['description'], \
                    feature['begin'], feature['end']
                    if start:
                        domains.append((dbd_type, start, stop))

        #there can be duplication, so I'm taking a set (also why I stored the
        #dna binding domain information as a tuple)
        for domain in set(domains):
            domain_output.append({'uniprot_id': accession,'dbd_type':domain[0],\
            'start':domain[1],'stop':domain[2]})
    #if there are no features, then the request object is printed out.
    except KeyError:
        print (r)
    return domain_output

def get_sequences(accessions, block_size = 100):
    '''Takes in a list of uniprot ids, (and possibly other things), and returns
    a dictionary mapping the ids to their sequences, as well as a list of
    invalid uniprot ids'''

    #removes invalid uniprot ids to avoid broken queries, will be output to the
    #user so they can be found or removed
    invalid_ids = [i for i in accessions if not re.match('[A-Z][\d]+', i) and
    not re.match('A0A0', i)]

    #if it's not invalid, it's ready to search!
    accs_to_search = [i.strip() for i in accessions if i not in invalid_ids]

    #just in case the user forgot to change the block_size or is not sure, this
    #will make it so the script doesn't break if the block_size is greater than
    #the number of searchable ids
    if block_size > len(accs_to_search):
        block_size  = len(accs_to_search)
    #avoiding zero division errors if there are no valid ids
    if not block_size:
        return None, accessions

    #Protein API url
    query_start = 'http://www.ebi.ac.uk/proteins/api/proteins?accession='

    #just in case, making sure the ids are unique to avoid repeated queries
    accs_to_search = list(set(accs_to_search))

    #getting the total number of queries to be performed
    num_queries =  ceil(len(accs_to_search)/block_size)
    seqs = {}
    for i in range(num_queries):
        #a little progress bar, since this function can run for a long time with
        #lots of entries to process.
        print('Query:' + str(i+1) + '/' + str(num_queries))
        start = i*block_size
        end = min(start+block_size, len(accs_to_search))

        #querying the first n = block_size ids
        query = query_start+'%2C'.join(accs_to_search[start:end])
        response = requests.get(query)

        #feeding the response into BeautifulSoup, a web parser
        s = soup(response.text, 'lxml')

        #if the query is broken, I will output the url, the error message (which
        #will tell the user which id is causing the error), and I will add the
        #ids in that query to the invalid_ids list, even if they are valid,
        #since their sequences will not be fetched this run.
        if not response.ok:
            invalid_ids += accs_to_search[start:end]
            error = ''
            for i in s.find('errormessage'):
                error += i.text+'\n'
            print(error)
            continue

        #parsing the response, each entry corresponds to a protein.
        proteins = s.findAll('entry')
        for p in proteins:
            if p.find('accession'):
                #getting the uniprot id of the protein in that entry
                acc = p.find('accession').text
                if p.find('sequence', {'length': re.compile('\d+')}):
                    #getting the sequence associated with that entry (the length
                    #field is needed since there are other sequence tags that
                    #don't actually have the sequence)
                    seqs[acc] = \
                    p.find('sequence', {'length': re.compile('\d+')}).text
                else:
                    seqs[acc] = ''
            else:
                #I'm not entirely sure this is a possible error mode, but if an
                #entry somehow doesn't contain a uniprot id, this will print out
                #the entry corresponding to that protein.
                print(p)
    return seqs, invalid_ids
