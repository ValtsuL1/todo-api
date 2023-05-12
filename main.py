from datetime import datetime
from fastapi import FastAPI, Response, Request
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
import os
import requests as req
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

api_key = os.environ.get("API_KEY")

con = sqlite3.connect("todos.sqlite", check_same_thread=False)

sql_create_todo_table = "CREATE TABLE IF NOT EXISTS todo(id INTEGER PRIMARY KEY, title VARCHAR, description VARCHAR, done INTEGER, created_at INTEGER)"

with con:
    con.execute(sql_create_todo_table)

class TodoItem(BaseModel):
    id: int
    title: str
    done: bool
    description: str
    created_at: int

class NewTodoItem(BaseModel):
    title: str
    description: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
def database_disconnect():
    con.close()

@app.get('/todos')
def get_todos(response:Response, done: bool | None = None):
    try:
        with con:
            if done != None:
                cur = con.execute("SELECT id, title, description, done, created_at FROM todo WHERE done = ?", (int(done),))
            else:
                cur = con.execute("SELECT id, title, description, done, created_at FROM todo")
            
            values: list[TodoItem] = []

            for item in cur.fetchall():
                id, title, description, done, created_at = item
                todo = TodoItem(id=id, title=title, description=description, done=done != 0, created_at=created_at)
                
                values.append(todo)

            return values
            
    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}

@app.get('/todos/{id}')
def get_todo_by_id(id:int, response: Response):
    try:
        with con:
            cur = con.execute("SELECT id, title, description, done, created_at FROM todo WHERE id = ?", (id,))

            result = cur.fetchone()

            if result == None:
                response.status_code = 404
                return {"err": f"Todo item with id {id} does not exist."}
            
            id, title, description, done, created_at = result

            return TodoItem(
                id=id,
                title=title,
                description=description,
                done=bool(done),
                created_at=created_at
            )
        
    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}

@app.post('/todos')
def create_todo(todo_item: NewTodoItem, response: Response):
    try:
        with con:
            dt = datetime.now()
            ts = int(datetime.timestamp(dt))

            cur = con.execute("INSERT INTO todo(title, description, done, created_at) VALUES(?, ?, ?, ?)", (todo_item.title, todo_item.description, int(False), ts,))

            response.status_code = 201

            return TodoItem(id=cur.lastrowid, title=todo_item.title, done=False, description=todo_item.description, created_at=ts)
    
    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}


@app.put('/todos/{id}')
def update_todo(id: int, todo_item: TodoItem, response: Response):
    try:
        with con:
            cur = con.execute(
                "UPDATE todo SET title = ?, description = ?, done = ? WHERE id = ? RETURNING *", (todo_item.title, todo_item.description, todo_item.done, id,))

            result = cur.fetchone()

            if result == None:
                response.status_code = 404
                return {"err": f"Todo item with id {id} does not exist"}
            
            id, title, description, done, created_at = result

            return TodoItem(
                id=id,
                title=title,
                description=description,
                done=bool(done),
                created_at=created_at
            )
        
    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}

@app.patch('/todos/{id}/done')
def update_todo_status(id: int, done: bool, response: Response):
    try:
        with con:
            cur = con.execute("UPDATE todo SET done = ? WHERE id = ? RETURNING done", (int(done), id,))

            result = cur.fetchone()

            if result == None:
                response.status_code = 404
                return {"err": f"Todo item with id {id} does not exist."}
            
            return {"done": bool(result[0])}

    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}

@app.delete('/todos/{id}')
def delete_todo(id: int, response: Response):
    try:
        with con:
            cur = con.execute("DELETE FROM todo WHERE id = ?", (id,))

            if cur.rowcount < 1:
                response.status_code = 404
                return {"err": f"Can't delete todo item, id {id} does not exist."}
            
            return "ok"
        
    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}
    
@app.get('/weather')
def get_current_weather(country: str, response: Response):
    try:
        # hakee pituus ja leveysasteet annetulle kaupungille
        location = req.get(f'http://api.openweathermap.org/geo/1.0/direct?q={country}&limit=1&appid={api_key}')

        location = location.json()

        # tallentaa pituus ja leveysasteet omiin muuttujiinsa
        lat = location[0]['lat']
        lon = location[0]['lon']

        # hakee säätiedot
        result = req.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}')

        result = result.json()

        weather = f'Lämpötila: {result["main"]["temp"]} °C Kosteus: {result["main"]["humidity"]} % Ilmanpaine: {result["main"]["pressure"]} hPa Tuulennopeus: {result["wind"]["speed"]} m/s'

        return weather

    except Exception as e:
        response.status_code = 500
        return {"err": str(e)}