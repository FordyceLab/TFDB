
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


class Protein_sequence(Base):

    __tablename__ = "protein_sequences"

    pid  = Column(Integer, primary_key=True , autoincrement = True)
    protein_name = Column(String)
    sequence = Column(String)
    info = relationship('TF_info', back_populates = 'protein_seqs')
    experiments = relationship('Experiment', back_populates = 'protein_seqs')
    protein_dbd_maps = relationship('DBD_TF_Maps', back_populates = 'protein_seqs')

    def __init__(self, protein_name, sequence):

        self.protein_name = protein_name
        self.sequence = sequence

class TF_info(Base):

    __tablename__ = 'protein_information'

    tf_id = Column(Integer, ForeignKey(Protein_sequence.pid), primary_key = True)
    tf_class = Column(String)
    family = Column(String)
    uniprot = Column(String)
    species = Column(String)
    protein_seqs = relationship('Protein_sequence', back_populates = 'info')

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
    protein_dbd_maps = relationship('DBD_TF_Maps', back_populates = 'DBD')

    def __init__(self, DBD_sequence , dbd_type):

        self.DBD_sequence = DBD_sequence
        self.dbd_type = dbd_type

    def __str__(self):
         return "{} {} {}".format(self.DBD_sequence, self.type)

class DBD_TF_Maps(Base):

    __tablename__ = 'DBD_TF_maps'
    #link_id = Column(Integer, autoincrement = True, primary_key = True)
    DBD_id = Column(Integer, ForeignKey(DBD.DBD_id), primary_key = True)
    protein_ids = Column(Integer, ForeignKey(Protein_sequence.pid), primary_key =True)


    protein_seqs= relationship('Protein_sequence', back_populates = 'protein_dbd_maps')
    DBD = relationship('DBD', back_populates = 'protein_dbd_maps')

    def __init__(self, protein, DBD):
        self.protein = protein
        self.DBD = DBD


class Experiment(Base):

    __tablename__ = 'experiment'

    experiment_id = Column(Integer, primary_key = True, autoincrement = True)
    protein_id = Column(Integer, ForeignKey(Protein_sequence.pid))
    pubmed_id = Column(String)
    assay = Column(String)
    protein_fragment = Column(String)
    
    protein_seqs = relationship('Protein_sequence', back_populates = 'experiments')
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
