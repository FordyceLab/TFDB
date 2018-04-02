select trans_factors.clone, trans_factors.gene_name, 
trans_factors.publication_id, trans_factors.species,
gene_ids.gene_id_name, clone_to_protseq.prot_sequence

from gene_ids
inner join trans_factors 
on trans_factors.gene_id = gene_ids.gene_id
inner join clone_to_protseq
on trans_factors.clone = clone_to_protseq.clone