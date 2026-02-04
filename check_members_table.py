from db_manager import DBManager

db = DBManager()
if db.connect():
    print("\nColumnas de la tabla 'Miembros':")
    print(db.get_table_columns("Miembros"))
    db.disconnect()
