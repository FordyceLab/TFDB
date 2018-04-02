select pfam_beta.pfam_acc, trans_factors.clone,
pfam_beta.pfam_id, pfam_beta.domain_seq, gene_ids.gene_id_name
from pfam_beta

inner join trans_factors
on pfam_beta.clone = trans_factors.clone
inner join gene_ids
on trans_factors.gene_id = gene_ids.gene_id
