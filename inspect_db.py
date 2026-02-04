import pyodbc
import os

db_path = os.path.join(os.getcwd(), 'Database.accdb')

try:
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        r"DBQ=" + db_path + ";"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    print(f"Conectado a la base de datos: {db_path}\n")

    # Listar tablas
    tables = []
    for table_info in cursor.tables(tableType='TABLE'):
        tables.append(table_info.table_name)

    if tables:
        print("Tablas encontradas:")
        for table_name in tables:
            print(f"- {table_name}")
            # Listar columnas para cada tabla
            columns = []
            for col_info in cursor.columns(table=table_name):
                columns.append(f"  - {col_info.column_name} ({col_info.type_name})")
            if columns:
                print("  Columnas:")
                for col in columns:
                    print(col)
            else:
                print("  No se encontraron columnas.")
            print()
    else:
        print("No se encontraron tablas en la base de datos.")

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    if sqlstate == '01000':
        print(f"Error de conexión: Asegúrese de tener instalado el controlador de Microsoft Access Database Engine (ACE OLEDB).")
        print(f"Puede descargarlo desde: https://www.microsoft.com/en-us/download/details.aspx?id=54920")
    else:
        print(f"Error al conectar o consultar la base de datos: {ex}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Conexión a la base de datos cerrada.")
