BABBELNET_QUERY = """
select t2.id, t3.ili, t1.wikidata from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
"""