import sqlite3
import requests
from langgraph.graph import StateGraph, START, END
from sentence_transformers import SentenceTransformer, util
from typing_extensions import TypedDict

from queries import ASSIGNED_ILIS_QUERY, REMAINING_WN_SYNSETS_QUERY

# Initialize the SentenceTransformer model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

def get_assigned_wikidata_ids(db_name: str):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(ASSIGNED_ILIS_QUERY)
    rows = cursor.fetchall()
    conn.close() 
    return [row[0] for row in rows]

assigned_wikidata_ids = get_assigned_wikidata_ids('wordnet_wikidata_mapping.db')

# Define the state structure
class State(TypedDict):
    db_name: str
    id: str
    ili: str
    label: str
    description: str
    wikidata: str
    wikidata_label: str
    wikidata_description: str
    score: str    

# Nodes
def query_wikidata(state: State):
    """Query Wikidata for entities matching the given label."""
    label = state["label"]
    query = f"""
    SELECT ?item ?itemLabel ?itemDescription WHERE {{
        ?item rdfs:label "{label}"@en.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 100
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/json"}
    response = requests.get(url, params={"query": query}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", {}).get("bindings", [])
        if results:
            for result in results:
                description = result.get("itemDescription", {}).get("value", "")
                if description and description.lower().strip() != 'wikimedia disambiguation page':
                    state["wikidata"].append(result["item"]["value"])
                    state["wikidata_label"].append(result["itemLabel"]["value"])
                    state["wikidata_description"].append(description)
    return state

def check_assigned_wikidata(state: State):
    """Check if the Wikidata URI is already assigned."""    
    if len(state['wikidata']) == 0:
        return "Fail"
    try:
        filtered_uri, filtered_label, filtered_description = zip(
            *[
                (x, y, z)
                for x, y, z in zip(state["wikidata"], state["wikidata_label"], state["wikidata_description"])
                if x not in assigned_wikidata_ids 
            ]
        )
    except ValueError:
        return "Fail"
    
    state["wikidata"] = list(filtered_uri)
    state["wikidata_label"] = list(filtered_label)
    state["wikidata_description"] = list(filtered_description)
    assert len(state['wikidata']) == len(state['wikidata_label']) == len(state['wikidata_description'])
    
    if len(state['wikidata']) == 0:
        return "Fail"
    return "Pass" 

def classify_similarity(state: State):
    """Check if the database label and description match the Wikidata label and description."""    
    wn_text = f"{state['label']}: {state['description']}"
    wn_embedding = model.encode(wn_text, convert_to_tensor=True)

    for wikidata_label, wikidata_description in zip(state["wikidata_label"], state["wikidata_description"]):        
        wikidata_text = f"{wikidata_label}: {wikidata_description}"    
        wikidata_embedding = model.encode(wikidata_text, convert_to_tensor=True)

        # Compute cosine similarity
        similarity = util.pytorch_cos_sim(wn_embedding, wikidata_embedding).item()
        state["score"].append(str(similarity))
    
    return state

def update_database(state: State):
    """Update the database with the Wikidata URI if a match is found."""
    conn = sqlite3.connect(state["db_name"])
    cursor = conn.cursor()
    for wikidata, wikidata_label, wikidata_description, score in zip(state["wikidata"], state["wikidata_label"], state["wikidata_description"], state["score"]):        
        cursor.execute(        
            "INSERT INTO remaining_wn_synsets_staging (id, ili, label, wikidata, wikidata_label, wikidata_description, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (state["id"], state["ili"], state["label"], wikidata, wikidata_label, wikidata_description, score),
        )
        conn.commit()
    conn.close()    
    return state

# Define the workflow
workflow = StateGraph(State)

workflow.add_node("query_wikidata", query_wikidata)
workflow.add_node("check_assigned_wikidata", check_assigned_wikidata)
workflow.add_node("classify_similarity", classify_similarity)
workflow.add_node("update_database", update_database)

workflow.add_edge(START, "query_wikidata")
workflow.add_conditional_edges(
    "query_wikidata", check_assigned_wikidata, {"Fail": END, "Pass": "classify_similarity"}
)   
workflow.add_edge("classify_similarity", "update_database")
workflow.add_edge("update_database", END)

chain = workflow.compile()

def process_database(db_name: str):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(REMAINING_WN_SYNSETS_QUERY)
    rows = cursor.fetchall()
    conn.close()

    for idx, row in enumerate(rows):
        id, ili, lemmas, description = row
        labels = lemmas.split(',')        
        for label in labels:
            state = {
                "db_name": db_name,
                "id": id,
                "ili": ili,
                "wikidata": [],
                "label": label.strip(),
                "description": description,
                "wikidata_label": [],
                "wikidata_description": [],
                "score": []            
            }
            try:
                state = chain.invoke(state)                                
            except Exception as e:
                print(f"Error processing row {id}: {e}")

        if idx % 100 == 0:
            print(f"Processed {idx} rows of {len(rows)}") 

def post_processing(db_name: str):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        select id, ili, wikidata, wikidata_label, wikidata_description, CAST(score as REAL) as final_score  
        from remaining_wn_synsets_staging
        where final_score > 0.8
        order by final_score desc
        """
    )
    rows = cursor.fetchall()
    conn.close()

    data_to_insert = []    
    for idx, row in enumerate(rows):
        id, ili, wikidata, wikidata_label, wikidata_description, final_score = row                    
        found_values = [item for item in data_to_insert if item[0] == id] + [item for item in data_to_insert if item[1] == ili] + [item for item in data_to_insert if item[2] == wikidata]
        if len(found_values) == 0:
            data_to_insert.append((id, ili, wikidata, wikidata_label, wikidata_description, str(final_score)))
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO remaining_wn_synsets (id, ili, wikidata, wikidata_label, wikidata_description, score) VALUES(?, ?, ?, ?, ?, ?)", data_to_insert)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    process_database('wordnet_wikidata_mapping.db')
    post_processing('wordnet_wikidata_mapping.db')