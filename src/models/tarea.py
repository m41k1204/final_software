import uuid
from typing import List, Dict

from .asignacion import Asignacion

class Tarea:
    ESTADOS_VALIDOS     = {"pendiente", "en_progreso", "finalizada"}

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        asignaciones: List[Asignacion] | None = None,
        estado: str = "pendiente",
        dependencias: List[str] | None = None,
        task_id: str | None = None,
    ):
        if estado not in self.ESTADOS_VALIDOS:
            raise ValueError("Estado inválido")
        self.id           = task_id or str(uuid.uuid4())
        self.nombre       = nombre
        self.descripcion  = descripcion
        self.estado       = estado
        self.asignaciones = asignaciones or []
        self.dependencias = dependencias or []     

    def add_asignacion(self, asignacion: Asignacion):
        self.asignaciones.append(asignacion)

    def set_estado(self, nuevo: str):
        if nuevo not in self.ESTADOS_VALIDOS:
            raise ValueError("Estado inválido")
        if self.estado == "finalizada" and nuevo != "finalizada":
            raise ValueError("No se puede volver a estados previos desde 'finalizada'")
        self.estado = nuevo

    def add_dependency(self, dep_id: str):
        if dep_id == self.id:
            raise ValueError("Una tarea no puede depender de sí misma")
        if dep_id in self.dependencias:
            raise ValueError("Dependencia ya existente")
        self.dependencias.append(dep_id)

    def remove_dependency(self, dep_id: str):
        if dep_id not in self.dependencias:
            raise ValueError("Dependencia inexistente")
        self.dependencias.remove(dep_id)

    def remove_asignacion(self, alias: str):
        if not any(a.usuario_alias == alias for a in self.asignaciones):
            raise ValueError("Usuario no asignado")      
        self.asignaciones = [
            a for a in self.asignaciones if a.usuario_alias != alias
        ]

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "asignaciones": [a.to_dict() for a in self.asignaciones],
            "dependencias": self.dependencias,                    
        }

    @staticmethod
    def from_dict(d: Dict) -> "Tarea":
        asignaciones = [Asignacion.from_dict(a) for a in d.get("asignaciones", [])]
        return Tarea(
            d["nombre"],
            d["descripcion"],
            asignaciones=asignaciones,
            estado=d.get("estado", "pendiente"),
            dependencias=d.get("dependencias", []),
            task_id=d["id"],
        )
