from abc import ABC, abstractmethod
from typing import List, Optional


class User:
    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

    def __repr__(self):
        return f"User(id={self.user_id}, name='{self.name}', email='{self.email}')"


class UserRepository(ABC):
    @abstractmethod
    def add_user(self, user: User) -> None:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        pass

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users:list[User] = []

    def add_user(self, user: User) -> None:
        self._users.append(user)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        for user in self._users:
            if user.user_id == user_id:
                return user            
        return None

    def get_all_users(self) -> List[User]:
        return self._users.copy()

    def delete_user(self, user_id: int) -> None:
        self._users = [user for user in self._users if user.user_id != user_id]


import sqlite3

class SQLiteUserRepository(UserRepository):
    def __init__(self, database: str):
        self.connection = sqlite3.connect(database)
        self._create_table()

    def _create_table(self):
        with self.connection as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            """)

    def add_user(self, user: User) -> None:
        with self.connection as conn:
            conn.execute("INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
                         (user.user_id, user.name, user.email))

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return User(*row) if row else None

    def get_all_users(self) -> List[User]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        rows = cursor.fetchall()
        return [User(*row) for row in rows]

    def delete_user(self, user_id: int) -> None:
        with self.connection as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

if __name__ == "__main__":
    # Skapa ett repository
    repo_choice = input("Välj 1 eller 2")
    if repo_choice == "1": 
        repository = InMemoryUserRepository()
    elif repo_choice == "2":
        repository = SQLiteUserRepository("user_master")

    # Lägg till användare
    repository.add_user(User(1, "Alice", "alice@example.com"))
    # repository.add_user(User(2, "Bob", "bob@example.com"))

    # Hämta alla användare
    print("Alla användare:", repository.get_all_users())

    # Hämta en specifik användare
    user = repository.get_user_by_id(1)
    print("Hämtad användare:", user)

    # Ta bort en användare
    repository.delete_user(1)
    print("Alla användare efter borttagning:", repository.get_all_users())