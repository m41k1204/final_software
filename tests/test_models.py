"""
Pruebas unitarias para Tareas, Usuarios y Asignacion. Los primeros 4 tests
son para los unit tests pedidos de 1 exito y 3 errores. El resto de unit tests son para que haya un code coverage del 100%

Se cubren:
1. Caso de ÉXITO      -> creación completa de los tres objetos
2. Caso de ERROR (#1) -> rol inválido en Asignacion
3. Caso de ERROR (#2) -> estado inválido en Tarea
4. Caso de ERROR (#3) -> dependencia duplicada en Tarea
"""

import pytest
from src.models.usuario import Usuario
from src.models.asignacion import Asignacion
from src.models.tarea import Tarea

def test_create_task_full_success():
    user = Usuario("1", "Ana", "ana@utec.edu")
    asign = Asignacion(user.email, "programador")
    tarea = Tarea("API", "CRUD completo")
    tarea.add_asignacion(asign)
    tarea.add_dependency("dep")

    assert tarea.to_dict()["estado"] == "pendiente"
    assert tarea.asignaciones[0].rol == "programador"
    assert "dep" in tarea.dependencias


def test_asignacion_rol_invalido():
    with pytest.raises(ValueError, match="Rol inválido"):
        Asignacion("ana@utec.edu", "gerente")      # rol NO existe


def test_tarea_estado_invalido():
    tarea = Tarea("API", "-")
    with pytest.raises(ValueError, match="Estado inválido"):
        tarea.set_estado("cancelada")               # estado NO existe


def test_tarea_dependencia_duplicada():
    tarea = Tarea("Módulo X", "-")
    tarea.add_dependency("dep")
    with pytest.raises(ValueError, match="Dependencia ya existente"):
        tarea.add_dependency("dep")             # duplicado

def test_usuario_y_asignacion_serializacion():
    u = Usuario("1", "Bruno", "bruno@utec.edu")
    d = u.get_user_info()
    assert d == {"id": "1", "name": "Bruno", "email": "bruno@utec.edu"}

    a1 = Asignacion("bruno@utec.edu", "infra")
    a2 = Asignacion.from_dict(a1.to_dict())
    assert a2.usuario_alias == "bruno@utec.edu" and a2.rol == "infra"

def test_tarea_remove_asignacion():
    t = Tarea("Mod X", "-")
    t.add_asignacion(Asignacion("ana@utec.edu", "pruebas"))
    t.remove_asignacion("ana@utec.edu")
    assert len(t.asignaciones) == 0
    with pytest.raises(ValueError, match="Usuario no asignado"):
        t.remove_asignacion("ana@utec.edu")

def test_tarea_set_estado_ok():
    t = Tarea("Back-end", "-")
    t.set_estado("en_progreso")
    assert t.estado == "en_progreso"


def test_tarea_dependencia_exito():
    t = Tarea("Mod Y", "-")
    t.add_dependency("dep")
    assert "dep" in t.dependencias
    t.remove_dependency("dep")
    assert "dep" not in t.dependencias

def test_tarea_estado_invalido_en_constructor():
    with pytest.raises(ValueError, match="Estado inválido"):
        Tarea("API", "-", estado="cancelada")

def test_tarea_dependencias_ramas_error():
    t = Tarea("Bug fix", "-")
    with pytest.raises(ValueError, match="sí misma"):
        t.add_dependency(t.id)
    with pytest.raises(ValueError, match="inexistente"):
        t.remove_dependency("foo-bar-baz")

def test_usuario_from_dict():
    data = {"id": "1", "name": "Zoe", "email": "zoe@utec.edu"}
    u = Usuario.from_dict(data)
    assert u.to_dict() == data

def test_tarea_estado_reversa_error():
    t = Tarea("Deploy", "-", estado="finalizada")
    with pytest.raises(ValueError, match="volver a estados previos"):
        t.set_estado("pendiente")          

def test_tarea_to_from_dict():
    original = Tarea("Doc", "Generar docs")
    original.add_dependency("dep-X")
    d = original.to_dict()
    clon = Tarea.from_dict(d)
    assert clon.to_dict() == d
