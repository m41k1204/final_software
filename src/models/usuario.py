class Usuario:
    def __init__(self, user_id: str, name: str, email: str):
        self.id = user_id
        self.name = name
        self.email = email

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "email": self.email}

    def get_user_info(self) -> dict:
        return self.to_dict()

    @staticmethod
    def from_dict(data: dict) -> "Usuario":
        return Usuario(data["id"], data["name"], data["email"])
