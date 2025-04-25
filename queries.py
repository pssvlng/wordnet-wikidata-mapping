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
select t4.id, t4.ili, t4.wikidata, t5.lemmas, t5.description from (
select * from cte1 where ili not in (select ili from cte2)
) as t4
inner join wn_all_synsets t5 on t5.id = t4.id
"""

REMAINING_WN_SYNSETS_QUERY = """
WITH cte1 AS (
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
UNION
SELECT ili from (
SELECT t1.ili, AVG(CAST(t1.score AS REAL)) AS final_score 
FROM yovisto_llm_as_a_judge t1
GROUP BY t1.id
having final_score > 0.575
order by final_score ASC
)
)
select * from wn_all_synsets where ili not in (select ili from cte1)
and SUBSTR(id, -1) = 'n';
"""

FINAL_DATASET_QUERY = """
select t2.id, t1.ili, t1.wikidata from john_wikidata t1 
INNER JOIN wn_all_synsets t2 on t2.ili = t1.ili
where t1.ili is not NULL
UNION
SELECT id, ili, wikidata from krasimir_wikidata where ili is not NULL
UNION 
SELECT t1.id, t1.ili, t1.wikidata from yovisto_wikidata_kea_annotator t1
inner join yovisto_wikidata_spotlight_annotator t2 on t1.ili = t2.ili
where t1.wikidata = t2.wikidata
UNION
select t2.id, t3.ili, t1.wikidata from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
UNION
SELECT ili, id, wikidata from (
SELECT t1.id, t1.ili, t1.wikidata, AVG(CAST(t1.score AS REAL)) AS final_score 
FROM yovisto_llm_as_a_judge t1
GROUP BY t1.id
having final_score > 0.575
order by final_score ASC
)
"""

ASSIGNED_ILIS_QUERY = """
select distinct(wikidata) from (
select t2.id, t1.ili, t1.wikidata from john_wikidata t1 
INNER JOIN wn_all_synsets t2 on t2.ili = t1.ili
where t1.ili is not NULL
UNION
SELECT id, ili, wikidata from krasimir_wikidata where ili is not NULL
UNION 
SELECT t1.id, t1.ili, t1.wikidata from yovisto_wikidata_kea_annotator t1
inner join yovisto_wikidata_spotlight_annotator t2 on t1.ili = t2.ili
where t1.wikidata = t2.wikidata
UNION
select t2.id, t3.ili, t1.wikidata from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
UNION
SELECT ili, id, wikidata from (
SELECT t1.id, t1.ili, t1.wikidata, AVG(CAST(t1.score AS REAL)) AS final_score 
FROM yovisto_llm_as_a_judge t1
GROUP BY t1.id
having final_score > 0.575
order by final_score ASC
)
)
"""

ALL_MAPPINGS_QUERY = """
select t2.id, t1.ili, t1.wikidata from john_wikidata t1 
INNER JOIN wn_all_synsets t2 on t2.ili = t1.ili
where t1.ili is not NULL
UNION
SELECT id, ili, wikidata from krasimir_wikidata where ili is not NULL
UNION 
SELECT t1.id, t1.ili, t1.wikidata from yovisto_wikidata_kea_annotator t1
inner join yovisto_wikidata_spotlight_annotator t2 on t1.ili = t2.ili
where t1.wikidata = t2.wikidata
UNION
select t2.id, t3.ili, t1.wikidata from babel_wn_30 t1 
inner join wn_30_wn_31 t2 on t1.identifier  = t2.identifier
inner join wn_all_synsets t3 on t3.Id = t2.id
UNION
SELECT ili, id, wikidata from (
SELECT t1.id, t1.ili, t1.wikidata, AVG(CAST(t1.score AS REAL)) AS final_score 
FROM yovisto_llm_as_a_judge t1
GROUP BY t1.id
having final_score > 0.575
order by final_score ASC
)
UNION
SELECT ili, id, wikidata from remaining_wn_synsets
"""