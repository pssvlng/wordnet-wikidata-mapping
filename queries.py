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
select ili from oewn_wikidata where ili is not NULL
UNION
SELECT ili from gf_wikidata where ili is not NULL
UNION 
SELECT t1.ili from yovisto_wikidata_kea_annotator t1
inner join yovisto_wikidata_spotlight_annotator t2 on t1.ili = t2.ili
where t1.wikidata = t2.wikidata
UNION
select t3.ili from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
)
select t4.id, t4.ili, t4.wikidata, t5.lemmas, t5.description from (
select * from cte1 where ili not in (select ili from cte2)
) as t4
inner join wn_all_synsets t5 on t5.id = t4.id
"""

REMAINING_WN_SYNSETS_QUERY = """
WITH cte1 AS (
select ili from oewn_wikidata where ili is not NULL
UNION
SELECT ili from gf_wikidata where ili is not NULL
UNION 
SELECT t1.ili from yovisto_wikidata_kea_annotator t1
inner join yovisto_wikidata_spotlight_annotator t2 on t1.ili = t2.ili
where t1.wikidata = t2.wikidata
UNION
select t3.ili from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
UNION
SELECT ili from yovisto_llm_as_a_judge
UNION
SELECT ili from remaining_wn_synsets
)
select * from wn_all_synsets where ili not in (select ili from cte1)
and SUBSTR(id, -1) = 'n';
"""

ASSIGNED_ILIS_QUERY = """
select distinct(wikidata) from (
select t2.id, t1.ili, t1.wikidata from oewn_wikidata t1 
INNER JOIN wn_all_synsets t2 on t2.ili = t1.ili
where t1.ili is not NULL
UNION
SELECT id, ili, wikidata from gf_wikidata where ili is not NULL
UNION 
SELECT t1.id, t1.ili, t1.wikidata from yovisto_wikidata_kea_annotator t1
inner join yovisto_wikidata_spotlight_annotator t2 on t1.ili = t2.ili
where t1.wikidata = t2.wikidata
UNION
select t2.id, t3.ili, t1.wikidata from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
UNION
SELECT id, ili, wikidata
FROM yovisto_llm_as_a_judge
UNION
SELECT id, ili, wikidata
FROM remaining_wn_synsets
)
"""

ALL_MAPPINGS_QUERY = """
select t2.id, t1.ili, t1.wikidata from oewn_wikidata t1 
INNER JOIN wn_all_synsets t2 on t2.ili = t1.ili
where t1.ili is not NULL
UNION
SELECT id, ili, wikidata from gf_wikidata where ili is not NULL
UNION 
SELECT t1.id, t1.ili, t1.wikidata from yovisto_wikidata_kea_annotator t1
inner join yovisto_wikidata_spotlight_annotator t2 on t1.ili = t2.ili
where t1.wikidata = t2.wikidata
UNION
select t2.id, t3.ili, t1.wikidata from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
UNION
SELECT id, ili, wikidata
FROM yovisto_llm_as_a_judge t1
UNION
SELECT ili, id, wikidata from remaining_wn_synsets
"""