# AlexKRotation: Notebooks and scripts for database collecting

**Quick Start:** 

This will allow you to build and clean the database completely from JSON files contained in this repo.
1. Run databasebuilder.ipynb (changing the directory/name as you see fit).

*Optional:* 
These will put in missing protein sequences and uniprot IDs, and fix some broken uniprot IDs from Jaspar.

2. Run missing_uniprot_ids.ipynb (changing directory)
3. Run filling_in_sequences.ipynb (changing directory)


**Description of Files**

-DB_setup.py: Current database schema created using SQLAlchemy's ORM. 

-Final_project_writeup.docx: Slightly outdated writeup on database, including outdated entity-relationship model and summary stats.

-database_builder.ipynb: Jupyter notebook to generate the database from jaspar_success.json and uniprobe_final.json files. If rebuilding from scratch, should still use this script (modify it to use new JSONs), since it accurately generates the relationships.

-filling_in_sequences.ipynb: Searches the database for proteins that have missing sequences and tries to get them from Uniprot using their Uniprot IDs, and updates the DB.

-jaspar_db_to_dict.py: If one has JASPAR built as a MySQL-style database on their computer, this will convert it into a JSON file that can be put into database_builder.

-jaspar_success.json: Most recent/complete JASPAR JSON file.

-missing_uniprot_ids.ipynb: Jupyter notebook that searches for missing Uniprot IDs in the database, finds them, and updates the DB.

-query1.sql: SQL query used in uniprobe_db_to_dict.py. Gets clone, sequence, (uniprobe internal) publication id, species, gene name, and gene mutant name (sometimes has information about partial constructs/mutations).

-query2_pfam.sql: SQL query used in uniprobe_db_to_dict.py. Some proteins have Pfam information in Uniprobe, this query gets the DNA binding domain sequence and type for these (as well as the Pfam ID, which is not currentlly used).

-query_dbds.sql: SQL query to get DNA binding domain sequences for some more proteins in Uniprobe. Only some mouse ones though... 

-query_publication_ids.sql: SQL query to get uniprobe publication IDs and the PWM folders associated with each publication.

-search_uniprot_ids.py: Contains the get_uniprot_ids function, which searches Uniprot for a gene name and an optional species name to get Uniprot IDs.

-tf.db: The current iteration of the database (SQLite).

-uniprobe_db_to_dict.py: If one has Uniprobe built as a MySQL-style database on their computer, this will convert it into a JSON file that can be put into database_builder.

-uniprobe_final.json: Most recent/complete Uniprobe JSON file.

-uniprobe_pubmed_ids.json: Contains a dictionary mapping Uniprobe internal publication IDs to Pubmed IDs.

-uniprobe_pwm_parser.py: Contains the function pwm_parser used in uniprobe_db_to_dict.py, which is used to read through Uniprobe's PWM files and get probability matrices, preferably generated using BEEML.

-uniprot_domains_sequences.py: Contains the functions get_domains and get_sequences, which get DNA binding domain information and protein sequences, respectively, using uniprot IDs, using the Proteins API from EMBL: https://www.ebi.ac.uk/proteins/api/doc/#/
