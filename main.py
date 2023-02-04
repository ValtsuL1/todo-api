from fastapi import FastAPI
from pydantic import BaseModel

# Pydantic katsoo tietotyypin pythonin tyyppivihjeestä
# FastAPI hyödyntää pydantic kirjastoa datan validoinnissa
class TodoItem(BaseModel):
    id: int       # id on kokonaisluku
    title: str    # title on tekstiä
    done: bool    # done on joko True tai False

app = FastAPI()

@app.get('/todos')
def get_todos(done: bool | None = None):
    if done != None:
        return f"Tässä palautetaan myöhemmin todot joiden done status on: {done}"
    return "Tässä palautetaan myöhemmin todo-lista"

@app.get('/todos/{id}')
def get_todo_by_id(id:int):
    # Palautetaan testimielessä funktiosta uusi TodoItem objekti.
    todo_item = TodoItem(id=id, title="testi", done=False)
    return todo_item

# @app.post('/todos') endpoint ottaa vastaan http POST metodilla tehdyn kyselyn (request).
# todo_item parametri sisältää tässä tapauksessa http bodyn 
# mukana tulevan JSON muotoisen datan. Pydantic kirjasto varmistaa että JSON
# data vastaa määriteltyä TodoItem luokkaa kun todo_item:lle on määritetty
# tyyppivihjeeksi TodoItem (ks. todo_item: TodoItem).
# FastAPI parsii JSON merkkijonon TodoItem objektiksi automaattisesti
# kun data on validoitu.
@app.post('/todos')
def create_todo(todo_item: TodoItem):
    # Tulostetaan komentoriville todo_item parametrista saatu data 
    print(todo_item)
    # Palautetaan testimielessä todo_item myös vastauksena.
    # Myöhemmin tässä funktiossa todo_item lisätään tietokantaan.
    return todo_item

@app.put('/todos/{id}')
def update_todo(id: int, todo_item: TodoItem):
    return f"Myöhemmin tässä korvataan tietokannassa olevaa todoitem uudella jonka id on {id}"

@app.patch('/todos/{id}')
def update_todo_status(id: int, todo_item: TodoItem):
    return f"Myöhemmin tässä muokataan tietokannassa olevaa todoitemiä jonka id on {id}"

@app.delete('/todos/{id}')
def delete_todo(id:int):
    return f"Myöhemmin tässä poistetaan tietokannasta todoitem jonka id on {id}"