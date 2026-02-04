from db_manager import DBManager

db = DBManager()
if db.connect():
    print("\nColumnas de la tabla 'Observaciones':")
    print(db.get_table_columns("Observaciones"))
    db.disconnect()
