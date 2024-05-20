from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from typing import List, Dict, Any

app = FastAPI()

# Configuración de CORS para permitir todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Configuración de la base de datos
host_name = "3.221.35.104"
port_number = "8005"
user_name = "root"
password_db = "utec"
database_name = "bd_api_atcoder"

# Definición del esquema User
class User(BaseModel):
    handle: str
    email: str
    rank: int
    rating: int
    user: str

# Obtener todos los usuarios
@app.get("/users", response_model=List[User])
def get_users():
    try:
        mydb = mysql.connector.connect(
            host=host_name,
            port=port_number,
            user=user_name,
            password=password_db,
            database=database_name
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        result = cursor.fetchall()
        mydb.close()
        return result
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")

# Obtener un usuario por ID
@app.get("/users/{handle}", response_model=User)
def get_user(handle: str):
    try:
        mydb = mysql.connector.connect(
            host=host_name,
            port=port_number,
            user=user_name,
            password=password_db,
            database=database_name
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE handle = %s", (handle,))
        result = cursor.fetchone()
        mydb.close()
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")

# Añadir un nuevo usuario
@app.post("/users", response_model=Dict[str, Any])
def add_user(user: User):
    try:
        mydb = mysql.connector.connect(
            host=host_name,
            port=port_number,
            user=user_name,
            password=password_db,
            database=database_name
        )
        cursor = mydb.cursor()
        sql = "INSERT INTO users (handle, email, rank, rating, user) VALUES (%s, %s, %s, %s, %s)"
        val = (user.handle, user.email, user.rank, user.rating, user.user)
        cursor.execute(sql, val)
        mydb.commit()
        mydb.close()
        return {"message": "User added successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")

# Modificar un usuario
@app.put("/users/{handle}", response_model=Dict[str, Any])
def update_user(handle: str, user: User):
    try:
        mydb = mysql.connector.connect(
            host=host_name,
            port=port_number,
            user=user_name,
            password=password_db,
            database=database_name
        )
        cursor = mydb.cursor()
        sql = "UPDATE users SET email=%s, rank=%s, rating=%s, user=%s WHERE handle=%s"
        val = (user.email, user.rank, user.rating, user.user, handle)
        cursor.execute(sql, val)
        mydb.commit()
        mydb.close()
        return {"message": "User modified successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")

# Eliminar un usuario por ID
@app.delete("/users/{handle}", response_model=Dict[str, Any])
def delete_user(handle: str):
    try:
        mydb = mysql.connector.connect(
            host=host_name,
            port=port_number,
            user=user_name,
            password=password_db,
            database=database_name
        )
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM users WHERE handle = %s", (handle,))
        mydb.commit()
        mydb.close()
        return {"message": "User deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error: {err}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
