BABBELNET_QUERY = """
select t2.id, t3.ili, t1.wikidata from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
"""

YOVISTO_COMBINED_QUERY = """
SELECT t1.ili, t1.wikidata, CAST(t1.score as FLOAT) + CAST(t2.score as FLOAT) as combined_score from yovisto_wikidata_kea_annotator t1
inner join yovisto_wikidata_spotlight_annotator t2 on t1.ili = t2.ili
where t1.wikidata = t2.wikidata
"""

LLM_AS_A_JUDGE_CANDICATE_QUERY = """
WITH cte1 AS (
SELECT id, ili, wikidata from yovisto_wikidata_kea_annotator
UNION
SELECT id, ili, wikidata from yovisto_wikidata_spotlight_annotator
),
cte2 AS (
select ili from john_wikidata where ili is not NULL
UNION
SELECT ili from krasimir_wikidata where ili is not NULL
UNION 
SELECT t1.ili from yovisto_wikidata_kea_annotator t1
inner join yovisto_wikidata_spotlight_annotator t2 on t1.ili = t2.ili
where t1.wikidata = t2.wikidata
UNION
select t3.ili from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
)
select * from cte1 where ili not in (select ili from cte2)
"""