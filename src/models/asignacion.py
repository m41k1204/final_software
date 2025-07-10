from datetime import datetime
from typing import Dict

class Asignacion:
    ROLES_VALIDOS = {"programador", "pruebas", "infra"}

    def __init__(self, usuario_alias: str, rol: str, fecha: str | None = None):
        if rol not in self.ROLES_VALIDOS:
            raise ValueError(f"Rol inválido: {rol}")
        self.usuario_alias = usuario_alias
        self.rol           = rol
        self.fecha         = fecha or datetime.utcnow().isoformat(timespec="seconds")

    def to_dict(self) -> Dict:
        return {
            "usuario_alias": self.usuario_alias,
            "rol": self.rol,
            "fecha": self.fecha,
        }

    @staticmethod
    def from_dict(d: Dict) -> "Asignacion":
        return Asignacion(d["usuario_alias"], d["rol"], d["fecha"])
