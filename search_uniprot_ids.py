#Extracting uniprot ids for the proteins missing them, both for their own both sake
#and for finding dna binding domains that are missing from the database
import requests
import re
from bs4 import BeautifulSoup as soup

def get_uniprot_id(protein, species = ''):
    '''Takes in protein name/other search term, and optionally a species name
    as strings, and returns a uniprot id'''
    #restricts results to genes, some proteins are not annotated as such
    gene_query = 'https://www.uniprot.org/uniprot/?query=gene:'

    #does not restrict to genes
    keyword_query = 'https://www.uniprot.org/uniprot/?query='

    #adding a filter for the organism to the query if the species is given
    if len(species):
        query_species = '&fil=Organism:'
    else:
        query_species = ''

    #getting only the column containing the uniprot ids
    columns= '&columns=id'
    #first query to try, searching for something annotated as a gene.
    query_site = gene_query + protein + query_species + species + columns
    r = requests.get(query_site)
    s = soup(r.text,'lxml')

    #finding the search results
    results = s.findAll('input', {'id': re.compile(r'check.*')})
    uniprot_search_results = []
    for result in results:
        uniprot = result['id'].split('_')[1]
        uniprot_search_results.append(uniprot)
    #if the previous query returned nothing, try a less strict query,
    #not requiring the search term to be a gene
    if not uniprot_search_results:
        query_site = keyword_query + protein + query_species + species + columns
        r = requests.get(query_site)
        s = soup(r.text,'lxml')
        results = s.findAll('input', {'id': re.compile(r'check.*')})
        for result in results:
            uniprot = result['id'].split('_')[1]
            uniprot_search_results.append(uniprot)
    if uniprot_search_results:
        return uniprot_search_results[0]
    # if no results were found, return None
    return None
