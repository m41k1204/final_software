# src/data_handler.py
import json
from pathlib import Path
from typing import List


from models.usuario import Usuario
from models.asignacion import Asignacion
from models.tarea import Tarea


class DataHandler:
    def __init__(self, filename: str = "data.json"):
        self.file = Path(filename)
        self.users: List[Usuario] = []
        self.tasks: list = []          
        self._load()

    def add_user(self, usuario: Usuario) -> None:
        if any(u.id == usuario.id or u.email == usuario.email for u in self.users):
            raise ValueError("Ya existe usuario con mismo id o email")
        self.users.append(usuario)
        self._save()

    def get_users(self) -> List[Usuario]:
        return self.users
    
    def add_task(self, tarea: Tarea) -> None:
        self.tasks.append(tarea)
        self._save()

    def get_tasks(self) -> List[Tarea]:
        return self.tasks

    def _save(self):
        payload = {
            "users": [u.to_dict() for u in self.users],
            "tasks": [t.to_dict() for t in self.tasks], 
        }
        with self.file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def _load(self):
        if not self.file.exists():
            return
        with self.file.open(encoding="utf-8") as f:
            data = json.load(f)
            self.users = [Usuario.from_dict(u) for u in data.get("users", [])]
            self.tasks = [Tarea.from_dict(t)   for t in data.get("tasks", [])]

    def find_user_by_email(self, email: str):
        return next((u for u in self.users if u.email == email), None)
    
    def find_task_by_id(self, task_id: str) -> Tarea | None:
        return next((t for t in self.tasks if t.id == task_id), None)

