import sys
from Bio.motifs.jaspar.db import JASPAR5
import re
import json
from uniprot_domains_sequences import get_sequences, get_domains
from jaspar_species_finder import get_species
from search_uniprot_ids import get_uniprot_id

#regex to capture valid dna binding domains
DBD_NAMES = re.compile(r'bHLH|bZIP|Homeo|HTH|WH|HMG|MADS|Helix|Leucine|DM\
    |AP2|TF|T-box|ctf|nfy|OB|Wor3|Dof|RHD|C2H2|H15|Paired|ETS|GATA|ARID|Zinc$\
    |DNA$|DNA-binding|TCP|H-T-H|ZN|Fork|IRF|WRKY|TEA|ATF|Nuclear|NHR', re.I)

DOMAIN_SEARCH_FIELDS = ['ZN_FING', 'DOMAIN', 'DNA_BIND', 'REGION']

JASPAR_DB_HOST = "127.0.0.1" #provided it's on your computer
JASPAR_DB_NAME = 'jaspar'
JASPAR_DB_USER = #username goes here
JASPAR_DB_PASS = #your password goes here
jdb = JASPAR5(
     host=JASPAR_DB_HOST,
     name=JASPAR_DB_NAME,
     user=JASPAR_DB_USER,
     password=JASPAR_DB_PASS
)
#creates motif objects out of all of the data in JASPAR.
motifs=jdb.fetch_motifs()

jaspardict = {}

#Making a dictionary out of the motifs for later storage as a json/searchability
for motif in motifs:
    jaspardict[motif.name]={'class':motif.tf_class,'family':motif.tf_family,
    'species':motif.species, 'acc':motif.acc,'pubmed':motif.medline,\
    'motif':motif.format("pfm"), 'type': motif.data_type}

#The biopython package gives uniprot taxonomical IDs instead of species names,
#so I'm adding in the species name as a value to the species key for each tf
#(but keeping the taxonomical id). get_species searches the taxonomical id
#on uniprot and gets the title of the page, which is the species name,
#returning a dictionary mapping species ids to species names.
species_dict = get_species(jaspardict)
for tf in jaspardict.values():
    species_ids =  ','.join(tf['species'])
    if species_ids in species_dict:
        tf['species'] = species_dict[species_ids]
#getting a list of (hopefully) uniprot ids from my jaspar database dictionary
#some entries in jaspar (such as complexes) have multiple uniprot ids, so I am
#splitting them up in uniprot_ids
uniprot_ids_per_protein = [tf['acc'] for tf in jaspardict.values()]
uniprot_ids = []
for acc in uniprot_ids_per_protein:
    for uniprot in acc:
        uniprot_ids.append(uniprot)
#removing duplicates for faster querying/fewer queries
unique_ids = list(set(uniprot_ids))

#Getting sequences for each of the proteins with uniprot ids using the
#protein api. With no block size set for get_sequences, this will break the data
#up into blocks of 100, the maximum query size with the protein API.
#This will return a dictionary mapping uniprot ids to sequences, as well as a
#list of all of the values in the 'acc' field that were not valid uniprot ids,
#or were batched with an id which broke a query.
sequence_dict, invalid_ids = get_sequences(unique_ids)

# trying to salvage the entries with invalid ids
bad_id_to_good = {}
for protein in invalid_ids:
    #since some good uniprot ids might be lumped in with the bad depending on
    #the block size, will try getting the sequences from the ids that look valid
    #before searching for its uniprot id
    if re.match('[A-Z][\d]+', protein):
        seq, invalid = get_sequences(protein, 1)
        if seq:
            sequence_dict[protein] = seq.values()
    else:
        #querying uniprot using it's REST API to get uniprot ids from whatever
        #weird thing they had in the database.
        uni_id = get_uniprot_id(protein)
        bad_id_to_good[protein] = uni_id
        seq, invalid = get_sequences(protein, 1)
        if seq:
            sequence_dict[uni_id] = [i for i in seq.values()][0]

entries_to_delete = []
for tf in jaspardict.values():
    sequence = ''
    for acc in tf['acc']:
        #switching the bad id to the good one if it was found
        if acc in bad_id_to_good:

            #if no uniprot id was found, adding the whole protein to a list to
            #delete
            if not bad_id_to_good[acc]:
                entries_to_delete.append(tf)

            #if it was, removing the bad id, putting in the good.
            tf['acc'].remove(acc)
            tf['acc'].append(bad_id_to_good[acc])
            acc = bad_id_to_good[acc]

        if acc in sequence_dict:
            #underscore added to split apart sequences of proteins
             sequence += sequence_dict[acc]+'_'
    #removing trailing underscore and adding sequence(s) to the dictionary
    tf['sequence'] = sequence[:-1]

#deleting entries with no valid uniprot ids
for key, tf in jaspardict.items():
    if tf in entries_to_delete:
        del jaspardict[key]

#getting DNA binding domains using the protein api
for tf in jaspardict.values():
    dbds = []
    for accession in tf['acc']:
        seq = None
        if accession in sequence_dict:
            seq = sequence_dict[accession]
        for dbd in get_domains(accession, DOMAIN_SEARCH_FIELDS, DBD_NAMES):
            if seq:
                try:
                    dbd['domain_sequence'] = seq[int(dbd['start'])-1:int(dbd['stop'])-1]
                except ValueError:
                    dbd['domain_sequence'] = 'unknown'
            dbds.append(dbd)
    tf['dbds'] = dbds

#dumping the dictionary to a json file
j=json.dumps(jaspardict, indent =4)
with open('jaspar_success.json','w') as f:
    print(j, file = f)
