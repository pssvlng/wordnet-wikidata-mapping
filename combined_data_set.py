import copy
import sqlite3
import requests
from queries import ALL_MAPPINGS_QUERY
import wn

def combine_data_sets(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(ALL_MAPPINGS_QUERY)
    rows = cursor.fetchall()
    conn.close()

    data_to_insert = []    
    for idx, row in enumerate(rows):
        id, ili, wikidata = row                    
        found_values = [item for item in data_to_insert if item[0] == id] + [item for item in data_to_insert if item[1] == ili] + [item for item in data_to_insert if item[2] == wikidata]
        if len(found_values) == 0:
            data_to_insert.append((id, ili, wikidata))
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO wordnet_wikidata_mappings_combined (id, ili, wikidata) VALUES(?, ?, ?)", data_to_insert)
    conn.commit()
    conn.close()

def get_wikidata_has_part_candidates2(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ili, wikidata FROM wordnet_wikidata_mappings_combined WHERE wikidata IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    lookups = copy.deepcopy(rows)
    has_part_data = []
    for idx, row in enumerate(rows):
        last_backslash_index = row[2].rfind('/')            
        q_id = row[2][last_backslash_index + 1:]

        query = f"""
        SELECT DISTINCT ?item ?itemLabel ?itemDescription WHERE {{        
            wd:{q_id} wdt:P527 ?item .        
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en". }}
        }}
        #LIMIT 100
        """
        url = "https://query.wikidata.org/sparql"
        headers = {"Accept": "application/json"}    
        response = requests.get(url, params={"query": query}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", {}).get("bindings", [])
                        
            if results:
                items = [result.get("item", {}).get("value", "") for result in results]
            else:
                items = []        

            try:    
                synset = wn.synset(f"o{row[0]}")
                for meronym in synset.meronyms():
                    hits = list(filter(lambda x: x[0] == meronym.id[1:], lookups))
                    for hit in hits:                    
                        if  hit[2] not in items:
                            #print((row[0], row[1], row[2], hit[2]))
                            has_part_data.append((row[0], row[1], synset.metadata()['subject'], meronym.id[1:], meronym.ili.id, meronym.metadata()['subject'], row[2], hit[2]))
            except Exception as e:
                print(f"Error processing synset for row {row[0]}: {e}")
                continue
        if (idx % 1000) == 0:
            print(f"Processed {idx} rows of {len(rows)}")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO wikidata_has_part_candidates2 (id, ili, category, id_part, ili_part, category_part, wikidata, has_part_candidate) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", has_part_data)
    conn.commit()
    conn.close()

def get_wikidata_has_part_candidates(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, ili, wikidata FROM wordnet_wikidata_mappings_combined WHERE wikidata IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    lookups = copy.deepcopy(rows)
    has_part_data = []
    for idx, row in enumerate(rows):
        last_backslash_index = row[2].rfind('/')            
        q_id = row[2][last_backslash_index + 1:]

        query = f"""
        SELECT DISTINCT ?item ?itemLabel ?itemDescription WHERE {{        
            wd:{q_id} wdt:P527 ?item .        
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en". }}
        }}
        #LIMIT 100
        """
        url = "https://query.wikidata.org/sparql"
        headers = {"Accept": "application/json"}    
        response = requests.get(url, params={"query": query}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", {}).get("bindings", [])
                        
            if results:
                items = [result.get("item", {}).get("value", "") for result in results]
            else:
                items = []        

            try:    
                synset = wn.synset(f"o{row[0]}")
                for meronym in synset.meronyms():
                    hits = list(filter(lambda x: x[0] == meronym.id[1:], lookups))
                    for hit in hits:                    
                        if  hit[2] not in items:
                            #print((row[0], row[1], row[2], hit[2]))
                            has_part_data.append((row[0], row[1], row[2], hit[2]))
            except Exception as e:
                print(f"Error processing synset for row {row[0]}: {e}")
                continue
        if (idx % 1000) == 0:
            print(f"Processed {idx} rows of {len(rows)}")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO wikidata_has_part_candidates (id, ili, wikidata, has_part_candidate) VALUES(?, ?, ?, ?)", has_part_data)
    conn.commit()
    conn.close()

#combine_data_sets('wordnet_wikidata_mapping.db')                        
#get_wikidata_has_part_candidates('wordnet_wikidata_mapping.db')
get_wikidata_has_part_candidates2('wordnet_wikidata_mapping.db')