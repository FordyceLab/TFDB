from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import sys
import json
from DB_setup import Protein_sequence, DBD, Experiment, PFM, TF_info, Base
from sqlalchemy.orm import sessionmaker


#setting up database directory, database will be named tf.db for now
db_directory = 'C:\\Users\\Alex\\Documents\\fordyce_rotation\\tf.db'

#setting up engine to connect to the database, using sqlite
engine = create_engine('sqlite:///'+db_directory)

Base.metadata.create_all(engine)

jaspar_file, uniprobe_file = ['jaspar_success.json', 'uniprobe_final.json']

with open(jaspar_file ,'r') as jasp:
    jaspar = json.loads(jasp.read())

with open(uniprobe_file ,'r') as uni:
    uniprobe = json.loads(uni.read())

import re
protein_seqs = []
experiments = []
pfms = []
protein_info = []
dbds = []

for tf, info in jaspar.items():
    protein_name = '_'.join(tf.split('::'))
    protein_seqs.append((protein_name, info['sequence']))
    uniprot_ids = str('_'.join(info['acc']))
    protein_info.append((protein_name, info['class'], info['family'],\
                                str(info['species']), uniprot_ids))
    experiments.append((protein_name, info['pubmed'], info['type'], \
                                   'FULL'))
    if not info['dbds']:
        dbds.append(('unknown', protein_name, 'unknown'))
    else:
        for dbd in info['dbds']:
            if 'domain_sequence' in dbd:
                dbd_seq = dbd['domain_sequence']
            else:
                dbd_seq = 'unknown'
            dbd_to_add = (dbd_seq, protein_name, dbd['dbd_type'])
            dbds.append(dbd_to_add)

    A, C, G, T, _ = info['motif'].split('\n')
    A = re.findall(r'[\d]+.[\d]+', A)
    C = re.findall(r'[\d]+.[\d]+', C)
    G = re.findall(r'[\d]+.[\d]+', G)
    T = re.findall(r'[\d]+.[\d]+', T)
    for pos in range(len(A)):
        pfms.append((protein_name, pos,float(A[pos]),\
                        float(C[pos]), float(G[pos]), float(T[pos])))

for protein in uniprobe.values():
    protein_name = protein['protein_mut']
    sequence = protein['sequence']
    uniprot = protein['uniprot']
    tf_class = 'unknown'
    family = 'unknown'
    species = protein['species']
    pubmed = protein['pubmed']
    pwm = protein['pwm']
    protein_seqs.append((protein_name, sequence))
    protein_info.append((protein_name, tf_class, family,\
                                species, uniprot))
    experiments.append((protein_name, pubmed, 'PBM', 'FULL'))
    if not protein['dbds']:
        dbds.append(('unknown', protein_name, 'unknown'))
    else:
        for dbd in protein['dbds']:
            if 'domain_sequence' in dbd:
                dbd_seq = dbd['domain_sequence']
            else:
                dbd_seq = 'unknown'
            dbd_to_add = (dbd_seq, protein_name, dbd['dbd_type'])
            dbds.append(dbd_to_add)
    for pos in range(len(pwm['A'])):
        A = pwm['A']
        C = pwm['C']
        G = pwm['G']
        T = pwm['T']
        pfms.append((protein_name, pos,float(A[pos]),\
                        float(C[pos]), float(G[pos]), float(T[pos])))

dbds2 = []
for i in set(dbds):
    dbds2.append(DBD(*i))

pfms2 = []
for i in set(pfms):
    pfms2.append(PFM(*i))

experiments2 = []
for i in set(experiments):
    experiments2.append(Experiment(*i))

protein_info2 = []
for i in set(protein_info):
    protein_info2.append(TF_info(*i))

protein_seqs2 = []
for i in set(protein_seqs):
    protein_seqs2.append((Protein_sequence(*i)))



Session = sessionmaker(bind=engine)
session = Session()
session.add_all(protein_seqs2)
session.add_all(experiments2)
session.add_all(pfms2)
session.add_all(protein_info2)
session.add_all(dbds2)
session.commit()
