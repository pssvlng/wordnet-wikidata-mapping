import sqlite3
import requests
from langgraph.graph import StateGraph, START, END
from sentence_transformers import SentenceTransformer, util
from typing_extensions import TypedDict

from queries import LLM_AS_A_JUDGE_CANDICATE_QUERY

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

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

def fetch_wikidata(state: State):
    """Fetch label and description from Wikidata"""
    wikidata_id = state["wikidata"].rsplit('/', 1)[-1]
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        entity_data = data["entities"][wikidata_id]
        state["wikidata_description"] = entity_data["descriptions"]["en"]["value"]
        try:
            state["wikidata_label"] = entity_data["labels"]["en"]["value"]
        except:
            state["wikidata_label"] = entity_data["labels"]["de"]["value"]                
    else:
        raise Exception(f"Failed to fetch data for Wikidata ID: {wikidata_id}")
    return state

def classify_entity(state: State):
    """Classify if the database entity matches the Wikidata entity"""
    # Compute embeddings for the database and Wikidata descriptions
    wn_text = f"{state['label']}: {state['description']}"
    wikidata_text = f"{state['wikidata_label']}: {state['wikidata_description']}"
    wn_embedding = model.encode(wn_text, convert_to_tensor=True)
    wikidata_embedding = model.encode(wikidata_text, convert_to_tensor=True)

    # Compute cosine similarity
    similarity = util.pytorch_cos_sim(wn_embedding, wikidata_embedding).item()
    state["score"] = str(similarity)    
    return state

def update_database(state: State):
    """Update the database with the verification result"""
    conn = sqlite3.connect(state["db_name"])
    cursor = conn.cursor()
    cursor.execute(        
        "INSERT INTO yovisto_llm_as_a_judge_staging (id, ili, label, wikidata, wikidata_label, wikidata_description, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (state["id"], state["ili"], state["label"], state["wikidata"], state["wikidata_label"], state["wikidata_description"], state["score"]),
    )
    conn.commit()
    conn.close()
    return state

workflow = StateGraph(State)
workflow.add_node("fetch_wikidata", fetch_wikidata)
workflow.add_node("classify_entity", classify_entity)
workflow.add_node("update_database", update_database)
workflow.add_edge(START, "fetch_wikidata")
workflow.add_edge("fetch_wikidata", "classify_entity")
workflow.add_edge("classify_entity", "update_database")
workflow.add_edge("update_database", END)

chain = workflow.compile()

def process_database(db_name:str):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(LLM_AS_A_JUDGE_CANDICATE_QUERY)
    rows = cursor.fetchall()
    conn.close()

    for idx, row in enumerate(rows):
        id, ili, wikidata, lemmas, description = row
        labels = lemmas.split(',')
        if len(labels) > 1:
            labels = labels + [lemmas]
        for label in labels:
            state = {
                "db_name": db_name,
                "id": id,
                "ili": ili,
                "wikidata": wikidata,
                "label": label.strip(),
                "description": description,
                "wikidata_label": "",
                "wikidata_description": "",
                "score": ""            
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
        SELECT t1.id, t1.ili, t1.wikidata, AVG(CAST(t1.score AS REAL)) AS final_score 
        FROM yovisto_llm_as_a_judge_staging t1
        GROUP BY t1.id
        having final_score > 0.575
        """
    )
    rows = cursor.fetchall()
    conn.close()

    data_to_insert = []    
    for idx, row in enumerate(rows):
        id, ili, wikidata, final_score = row                    
        found_values = [item for item in data_to_insert if item[0] == id] + [item for item in data_to_insert if item[1] == ili] + [item for item in data_to_insert if item[2] == wikidata]
        if len(found_values) == 0:
            data_to_insert.append((id, ili, wikidata, str(final_score)))
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO yovisto_llm_as_a_judge (id, ili, wikidata, score) VALUES(?, ?, ?, ?)", data_to_insert)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    process_database('wordnet_wikidata_mapping.db')
    post_processing('wordnet_wikidata_mapping.db')
