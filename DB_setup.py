from sqlalchemy import Column, Integer, String, Float, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

#setting up database directory, database will be named tf.db for now
#db_directory = 'C:\\Users\\Alex\\Documents\\fordyce_rotation\\tf.db'

#setting up engine to connect to the database, using sqlite
#engine = create_engine('sqlite:///'+db_directory, echo=True)

#setting up base
Base = declarative_base()

#making classes for each table in tf.db

class Clone_sequence(Base):

    __tablename__ = "Clone_sequence"

    clone_id  = Column(Integer, primary_key=True , autoincrement = True)
    clone_name = Column(String)
    sequence = Column(String)
    #info = relationship('TF_info', back_populates = 'protein_seqs')
    experiments = relationship('Experiment', back_populates = 'protein_seqs')
    clone_dbd_maps = relationship('DBD_Clone_Maps', back_populates = 'seqs')
    clone_protein_map = relationship('Protein_clone_map', back_populates = 'clones')

    def __init__(self, clone_name, sequence):

        self.clone_name = clone_name
        self.sequence = sequence

class TF_info(Base):

    __tablename__ = 'protein_information'

    uniprot = Column(String, primary_key = True)
    tf_class = Column(String)
    family = Column(String)
    species = Column(String)
    clone_protein_map = relationship('Protein_clone_map', back_populates = 'proteins')

    def __init__(self, tf_class, family, species, uniprot):
        self.tf_class = tf_class
        self.family = family
        self.species = species
        self.uniprot = uniprot

class DBD(Base):

    __tablename__ = 'dbd'

    DBD_id = Column(Integer, primary_key = True, autoincrement = True)
    DBD_sequence = Column(String)
    dbd_type = Column(String)
    clone_dbd_maps = relationship('DBD_Clone_Maps', back_populates = 'DBD')

    def __init__(self, DBD_sequence , dbd_type):

        self.DBD_sequence = DBD_sequence
        self.dbd_type = dbd_type

    def __str__(self):
         return "{} {} {}".format(self.DBD_sequence, self.type)

class DBD_Clone_Maps(Base):

    __tablename__ = 'DBD_clone_map'
    #link_id = Column(Integer, autoincrement = True, primary_key = True)
    DBD_id = Column(Integer, ForeignKey(DBD.DBD_id), primary_key = True)
    protein_ids = Column(Integer, ForeignKey(Clone_sequence.clone_id), primary_key =True)
    seqs= relationship('Clone_sequence', back_populates = 'clone_dbd_maps')
    DBD = relationship('DBD', back_populates = 'clone_dbd_maps')

    def __init__(self, protein, DBD):
        self.protein = protein
        self.DBD = DBD

class Protein_clone_map(Base):

    __tablename__ = 'clone_protein_map'

    clone_id = Column(Integer, ForeignKey(Clone_sequence.clone_id), primary_key = True)
    uniprot = Column(String, ForeignKey(TF_info.uniprot), primary_key = True)
    clones = relationship('Clone_sequence', back_populates = 'clone_protein_map')
    proteins = relationship('TF_info', back_populates = 'clone_protein_map')

    def __init__(self, clone, protein):
        self.protein = protein
        self.clone = clone

class Experiment(Base):

    __tablename__ = 'experiment'

    experiment_id = Column(Integer, primary_key = True, autoincrement = True)
    clone_id = Column(Integer, ForeignKey(Clone_sequence.clone_id))
    pubmed_id = Column(String)
    assay = Column(String)
    protein_fragment = Column(String)
    protein_seqs = relationship('Clone_sequence', back_populates = 'experiments')
    pfms = relationship('PFM', back_populates = 'experiments')

    def __init__(self, pubmed_id, assay, protein_fragment = 'full'):

        self.pubmed_id = pubmed_id
        self.assay = assay
        self.protein_fragment = protein_fragment

    def __str__(self):
        return "{} {} {} {}".format(self.protein_name, self.pubmed_id, self.assay, self.protein_fragment)

class PFM(Base):

    __tablename__ = 'pfm'
    eid = Column(Integer, ForeignKey(Experiment.experiment_id), primary_key = True)
    position = Column(Integer, primary_key = True)
    a = Column(Float)
    c = Column(Float)
    g = Column(Float)
    t = Column(Float)
    db = Column(String)
    experiments = relationship('Experiment', back_populates = 'pfms')


    def __init__(self, position, a, c, g, t, db):
        self.position = position
        self.a = a
        self.c = c
        self.g = g
        self.t = t
        self.db = db

