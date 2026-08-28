import os

from sqlalchemy import create_engine

db_path = os.path.expanduser("~/Sites/chessclub/db.sqlite3")

engine = create_engine(f"sqlite:///{db_path}")
