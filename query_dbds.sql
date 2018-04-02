select trans_factors.clone,
gene_ids.gene_id_name, dbds.seq

from dbds
inner join gene_ids 
on dbds.gene_name = gene_ids.gene_name
inner join trans_factors
on trans_factors.gene_id = gene_ids.gene_id