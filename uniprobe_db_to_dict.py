import pymysql
import os
import sqlalchemy as sa
import re
import json
from uniprobe_pwm_parser import pwm_parser
from search_uniprot_ids import get_uniprot_id
from uniprot_domains_sequences import get_domains

DBD_NAMES = re.compile(r'bHLH|bZIP|Homeo|HTH|WH|HMG|MADS|Helix|Leucine|DM\
    |AP2|TF|T-box|ctf|nfy|OB|Wor3|Dof|RHD|C2H2|H15|Paired|ETS|GATA|ARID|Zinc$\
    |DNA$|DNA-binding|TCP|H-T-H|ZN|Fork|IRF|WRKY|TEA|ATF|Nuclear|NHR', re.I)

DOMAIN_SEARCH_FIELDS = ['ZN_FING', 'DOMAIN', 'DNA_BIND', 'REGION']

engine = sa.create_engine('mysql+pymysql://root:tomato1393@127.0.0.1/uniprobe')
conn = engine.connect()
meta = sa.MetaData()
meta.reflect(engine)

#query to get clone, sequence, uniprobe pub id, species, protein, protein_mut
#(full name, including mutations)
uniprobe_dict = {}
with(open('query1.sql')) as q:
    query_protein_info = q.read()

proteins = conn.execute(query_protein_info)


for result in proteins:
    uniprobe_dict[result.clone] = {'sequence': result.prot_sequence,
    'pubid': result.publication_id,
    'species': result.species,
    'protein': result.gene_name,
    'protein_mut': result.gene_id_name}

#some proteins have pfam domains, if they do, getting the pfam id, which is the
#dna binding domain type, as well as the domain sequence and pfam id
with open('query2_pfam.sql') as q:
    query_pfam = q.read()

clone_domains = conn.execute(query_pfam)

for uni in uniprobe_dict.values():
    uni['dbds'] = []
for result in clone_domains:
    uniprobe_dict[result.clone]['dbds'].append({'domain_sequence': result.domain_seq,
     'dbd_type':result.pfam_id, 'pfam_acc':result.pfam_acc})


#some proteins (specifically mouse ones) have their domain sequences stored in
#uniprobe, but with no dna binding domain type information
with open('query_dbds.sql') as q:
    query_mouse_dbds = q.read()

mouse_dbds = conn.execute(query_mouse_dbds)
genelist = []
for result in mouse_dbds:
    #if the dbds are already populated by the pfam query, I don't want to remove
    #that information, since it has information on the dbd type
    dbd_list = uniprobe_dict[result.clone]['dbds']
    if not dbd_list:
        uniprobe_dict[result.clone]['dbds'].append({'domain_sequence': result.seq,
        'dbd_type': ''})

print('Queries done')

#getting Uniprot IDs if possible, if not, deleting the entry
removal_list = []
for clone, protein in uniprobe_dict.items():
    uniprot = get_uniprot_id(protein['protein'], protein['species'])
    print(uniprot)
    if uniprot:
        protein['uniprot'] = uniprot
    else:
        removal_list.append(clone)
for clone in removal_list:
    del uniprobe_dict[clone]
print ('DB cleaned')
for protein in uniprobe_dict.values():
    if not len(protein['dbds']):
        dbds = []
        accession = protein['uniprot']
        seq = protein['sequence']
        for dbd in get_domains(accession, DOMAIN_SEARCH_FIELDS, DBD_NAMES):
            if seq:
                try:
                    dbd['domain_sequence'] = seq[int(dbd['start'])-1:int(dbd['stop'])-1]
                except ValueError:
                    dbd['domain_sequence'] = 'unknown'
            dbds.append(dbd)
            print(dbd)
    protein['dbds'] = dbds

with open('uniprobe_pubmed_ids.json', 'r') as pids:
    pubmeds = json.loads(pids.read())
with open('query_publication_ids.sql') as q:
    query_pub_ids = q.read()

pubmeds_to_pfm_folders = conn.execute(query_pub_ids)

pubid_to_folder = {}
for result in pubmeds_to_pfm_folders:
    pubid_to_folder[result.publication_id] = result.folder_name

for info in uniprobe_dict.values():
    uniprobe_pubid = info['pubid']
    info['pubmed'] = pubmeds[str(uniprobe_pubid)]
    info['folder'] = pubid_to_folder[uniprobe_pubid]

print('about to get the pfms')

import os
from uniprobe_pwm_parser import pwm_parser

root_dir = '.\\UNIPROBE_PWMS'
pwm_folders = os.listdir(root_dir)

for gene, info in uniprobe_dict.items():
    pub_folder = os.path.join(root_dir, info['folder'])
    pwm_files = os.listdir(pub_folder)
    for pwm_file in pwm_files:
        if re.search(info['protein_mut'], pwm_file, flags = re.I):
            print(info['protein'], info['protein_mut'], pwm_file)
            if 'pwm' in info and not re.search('bml', pwm_file):
                continue
            pdict = pwm_parser(pub_folder, pwm_file)
            info['pwm'] = pdict

for protein in uniprobe_dict.values():
    del protein['pubid']

deletion_list = []
for clone, protein in uniprobe_dict.items():
    if 'pwm' not in protein:
        deletion_list.append(clone)
    elif not len(protein['pwm']):
        deletion_list.append(clone)

for protein in deletion_list:
    del uniprobe_dict[protein]

u  = json.dumps(uniprobe_dict)
with open ('uniprobe_final.json', 'w') as uni:
    print(u, file = uni)

    
