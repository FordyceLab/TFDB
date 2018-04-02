
from sqlalchemy import Column, Integer, String, Float, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

#setting up database directory, database will be named tf.db for now
#db_directory = 'C:\\Users\\Alex\\Documents\\fordyce_rotation\\tf.db'

#setting up engine to connect to the database, using sqlite
#engine = create_engine('sqlite:///'+db_directory, echo=True)

#setting up base
Base = declarative_base()

#making classes for each table in tf.db
class Protein_sequence(Base):

    __tablename__ = "protein_sequences"

    pid  = Column(Integer, Sequence('pid_seq', metadata=Base.metadata), primary_key=True)
    protein_name = Column(String)
    sequence = Column(String)
    dbds = relationship('DBD')

    def __init__(self,protein_name, sequence):

        self.protein_name =protein_name
        self.sequence = sequence

class DBD(Base):

    __tablename__ = 'dbd'

    DBD_sequence = Column(String, primary_key = True)
    dbd_type = Column(String)
    protein_name = Column(String, ForeignKey('protein_sequences.pid'))

    def __init__(self, DBD_sequence ,protein_name, dbd_type):

        self.DBD_sequence = DBD_sequence
        self.protein_name =protein_name
        self.dbd_type = dbd_type

    def __str__(self):
         return "{} {} {}".format(self.DnaBD, self.protein_name, self.type)


class Experiment(Base):

    __tablename__ = 'experiment'

    experiment_id = Column(Integer, primary_key = True, autoincrement = True)
    protein_name = Column(String)
    pubmed_id = Column(String)
    assay = Column(String)
    protein_fragment = Column(String)

    def __init__(self,protein_name, pubmed_id, assay, protein_fragment):

        self.protein_name =protein_name
        self.pubmed_id = pubmed_id
        self.assay = assay
        self.protein_fragment = protein_fragment
    def __str__(self):
        return "{} {} {} {}".format(self.protein_name, self.pubmed_id, self.assay, self.protein_fragment)

class PFM(Base):

    __tablename__ = 'pfm'
    pfm_id = Column(Integer, primary_key = True, autoincrement = True)
    protein_name = Column(String)
    position = Column(Integer)
    a = Column(Float)
    c = Column(Float)
    g = Column(Float)
    t = Column(Float)
    tag = Column(String)

    def __init__(self,protein_name, position, a, c, g, t):
        self.protein_name =protein_name
        self.position = position
        self.a = a
        self.c = c
        self.g = g
        self.t = t

class TF_info(Base):

    __tablename__ = 'protein_information'

    tf_id = Column(Integer, primary_key = True, autoincrement = True)
    protein_name = Column(String)
    tf_class = Column(String)
    family = Column(String)
    uniprot = Column(String)
    species = Column(String)

    def __init__(self,protein_name, tf_class, family, species, uniprot):
        self.protein_name =protein_name
        self.tf_class = tf_class
        self.family = family
        self.species = species
        self.uniprot = uniprot
