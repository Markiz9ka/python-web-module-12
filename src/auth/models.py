
import sqlalchemy
import sqlalchemy.orm as orm
import database

class User(database.Base):
    __tablename__ = "users"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(20), unique=True)
    hash_password: orm.Mapped[str]
    refresh_token: orm.Mapped[str | None] = orm.mapped_column(sqlalchemy.String(255))
    contacts: orm.Mapped[list["Contacts"]] = orm.relationship(
        "Contacts", back_populates="user", cascade="all, delete-orphan"
    )