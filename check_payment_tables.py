from db_manager import DBManager

db = DBManager()
if db.connect():
    print("\nColumnas de la tabla 'Pagos':")
    print(db.get_table_columns("Pagos"))

    print("\nColumnas de la tabla 'Pago-Mensual':")
    print(db.get_table_columns("Pago-Mensual"))

    print("\nColumnas de la tabla 'Pago-Quincenal':")
    print(db.get_table_columns("Pago-Quincenal"))
    
    db.disconnect()
