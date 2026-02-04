import pyodbc
import os
import sys # Importar sys
from datetime import datetime

class DBManager:
    def __init__(self, db_name='Database.accdb'):
        # Usar una carpeta de usuario para la base de datos (siempre editable y sin problemas de permisos)
        from pathlib import Path
        import shutil
        import getpass
        user_dir = os.path.join(os.environ.get('APPDATA') or os.path.expanduser('~'), 'HappyBodyGym')
        os.makedirs(user_dir, exist_ok=True)
        self.db_path = os.path.join(user_dir, db_name)
        # Si la base de datos no existe en la carpeta de usuario, copiarla desde el directorio de instalación
        if not os.path.exists(self.db_path):
            # Buscar la base de datos original junto al ejecutable o en la carpeta de instalación
            if getattr(sys, 'frozen', False):
                orig_db = os.path.join(os.path.dirname(sys.executable), db_name)
            else:
                orig_db = os.path.join(os.getcwd(), db_name)
            if os.path.exists(orig_db):
                shutil.copy2(orig_db, self.db_path)
        self.conn = None
        self.cursor = None
        self.conn_str = ( # Initialize conn_str here
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            r"DBQ=" + self.db_path + ";"
        )

    def connect(self):
        try:
            self.conn = pyodbc.connect(self.conn_str)
            self.cursor = self.conn.cursor()
            print("Conexión a la base de datos establecida.")
            self.create_fortnightly_payment_table() # Llamar a la función para crear la tabla
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            if sqlstate == '01000':
                print(f"Error de conexión: Asegúrese de tener instalado el controlador de Microsoft Access Database Engine (ACE OLEDB).")
                print(f"Puede descargarlo desde: https://www.microsoft.com/en-us/download/details.aspx?id=54920")
            else:
                print(f"Error al conectar a la base de datos: {ex}")
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print("Conexión a la base de datos cerrada.")

    def fetch_all(self, table_name):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM [{table_name}]")
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except pyodbc.Error as ex:
            print(f"Error al obtener datos de la tabla {table_name}: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_all_observations(self):
        """Obtiene todas las observaciones de la base de datos."""
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            query = "SELECT O.[ID-Observac], O.[ID-Miembro], M.Nombre, M.Apellido, O.Observacion, O.[Fecha de nacimiento] AS Fecha FROM Observaciones AS O INNER JOIN Miembros AS M ON O.[ID-Miembro] = M.[ID-Miembro] ORDER BY O.[Fecha de nacimiento] DESC"
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            observations = []
            for row in cursor.fetchall():
                observations.append(dict(zip(columns, row)))
            return observations
        except pyodbc.Error as ex:
            print(f"Error al obtener todas las observaciones: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def execute_query(self, query, params=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            print(f"Ejecutando consulta: {query}")
            print(f"Con parámetros: {params}")
            cursor.execute(query, params or ())
            conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # --- Funciones específicas para Miembros ---
    def get_table_columns(self, table_name):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.columns(table=table_name)
            columns = []
            for col_info in cursor.fetchall():
                columns.append(col_info.column_name)
            return columns
        except pyodbc.Error as ex:
            print(f"Error al obtener columnas de la tabla {table_name}: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def add_member(self, nombre, apellido, cedula, telefono):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            query = "INSERT INTO Miembros (Nombre, Apellido, Cedula, Telefono) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (nombre, apellido, cedula, telefono))
            conn.commit()
            # Obtener el ID del último registro insertado (para campos autonuméricos en Access)
            cursor.execute("SELECT @@IDENTITY")
            row = cursor.fetchone()
            if row and row[0] is not None:
                new_id = row[0]
                return int(new_id)
            else:
                print("No se pudo obtener el ID del nuevo miembro.")
                return None
        except Exception as e:
            print(f"Error al añadir miembro o obtener el ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def add_observation(self, miembro_id, observacion, fecha_nacimiento=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            if fecha_nacimiento:
                query = "INSERT INTO Observaciones ([ID-Miembro], Observacion, [Fecha de nacimiento]) VALUES (?, ?, ?)"
                cursor.execute(query, (miembro_id, observacion, fecha_nacimiento))
            else:
                query = "INSERT INTO Observaciones ([ID-Miembro], Observacion) VALUES (?, ?)"
                cursor.execute(query, (miembro_id, observacion))
            conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al añadir observación: {ex}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_members(self):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT M.[ID-Miembro], M.Nombre, M.Apellido, M.Cedula, M.Telefono FROM Miembros AS M")
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except pyodbc.Error as ex:
            print(f"Error al obtener datos de la tabla Miembros: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_member_by_id(self, member_id):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            query = "SELECT [ID-Miembro], Nombre, Apellido, Cedula, Telefono FROM Miembros WHERE [ID-Miembro] = ?"
            cursor.execute(query, (member_id,))
            columns = [column[0] for column in cursor.description]
            row = cursor.fetchone()
            if row:
                return dict(zip(columns, row))
            return None
        except pyodbc.Error as ex:
            print(f"Error al obtener miembro por ID: {ex}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_member_by_cedula(self, cedula):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            query = "SELECT [ID-Miembro] AS ID, Nombre, Apellido, Cedula, Telefono FROM Miembros WHERE Cedula = ?"
            cursor.execute(query, (cedula,))
            columns = [column[0] for column in cursor.description]
            row = cursor.fetchone()
            if row:
                return dict(zip(columns, row))
            return None
        except pyodbc.Error as ex:
            print(f"Error al obtener miembro por cédula: {ex}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # --- Funciones específicas para Asistencia ---
    def record_attendance(self, miembro_id, fecha_hora=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            if fecha_hora is None:
                fecha_hora = datetime.now()
            query = "INSERT INTO Asistencia ([ID-Miembro], fechaAsistencia) VALUES (?, ?)"
            cursor.execute(query, (miembro_id, fecha_hora))
            conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al registrar asistencia: {ex}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_attendance(self, miembro_id=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            if miembro_id:
                query = "SELECT [ID-Asistencia], [ID-Miembro], fechaAsistencia FROM Asistencia WHERE [ID-Miembro] = ? ORDER BY fechaAsistencia DESC"
                cursor.execute(query, (miembro_id,))
            else:
                query = "SELECT [ID-Asistencia], [ID-Miembro], fechaAsistencia FROM Asistencia ORDER BY fechaAsistencia DESC"
                cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            print(f"Columnas recuperadas en get_attendance: {columns}")
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except pyodbc.Error as ex:
            print(f"Error al obtener asistencia: {ex}")
            return []
        except Exception as e:
            print(f"Error inesperado en get_attendance: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_attendance_by_date(self, date):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            date_str = date.strftime("%Y-%m-%d")
            query = """
            SELECT A.[ID-Asistencia], A.[ID-Miembro], A.fechaAsistencia, M.Nombre, M.Apellido, M.Cedula
            FROM Asistencia AS A
            INNER JOIN Miembros AS M ON A.[ID-Miembro] = M.[ID-Miembro]
            WHERE Format(A.fechaAsistencia, 'yyyy-mm-dd') = ?
            ORDER BY A.fechaAsistencia DESC
            """
            cursor.execute(query, (date_str,))
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            results = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                if 'fechaAsistencia' in row_dict:
                    row_dict['Hora'] = row_dict.pop('fechaAsistencia')
                results.append(row_dict)
            return results
        except pyodbc.Error as ex:
            print(f"Error al obtener asistencia por fecha: {ex}")
            return []
        except Exception as e:
            print(f"Error inesperado en get_attendance_by_date: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # --- Funciones específicas para Pagos ---
    def add_payment(self, miembro_id, monto, fecha_pago, tipo_membresia, tipo_moneda, referencia=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            query = "INSERT INTO Pagos ([ID-Miembros], [Fecha-Pago], [Efectivo-$], [Efectivo-Bs], [Monto-Digital-Bs], Referencia) VALUES (?, ?, ?, ?, ?, ?)"
            
            efectivo_usd = 0.0
            efectivo_bs = 0.0
            monto_digital_bs = 0.0

            if tipo_moneda == "$":
                efectivo_usd = monto
            elif tipo_moneda == "Bs":
                efectivo_bs = monto
            elif tipo_moneda == "Monto Digital":
                monto_digital_bs = monto

            full_referencia = f"Tipo Membresía: {tipo_membresia}"
            if referencia:
                full_referencia += f", Ref: {referencia}"

            cursor.execute(query, (miembro_id, fecha_pago, efectivo_usd, efectivo_bs, monto_digital_bs, full_referencia))
            conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al añadir pago: {ex}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_payments(self, miembro_id=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            if miembro_id:
                query = "SELECT [ID-Pagos], [ID-Miembros], [Fecha-Pago], [Efectivo-$], [Efectivo-Bs], [Monto-Digital-Bs], Referencia, Abono, Resto FROM Pagos WHERE [ID-Miembros] = ? ORDER BY [Fecha-Pago] DESC"
                cursor.execute(query, (miembro_id,))
            else:
                query = "SELECT [ID-Pagos], [ID-Miembros], [Fecha-Pago], [Efectivo-$], [Efectivo-Bs], [Monto-Digital-Bs], Referencia, Abono, Resto FROM Pagos ORDER BY [Fecha-Pago] DESC"
                cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except pyodbc.Error as ex:
            print(f"Error al obtener pagos: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_payments_by_member(self, member_id):
        """Obtiene todos los pagos de un miembro específico."""
        return self.get_payments(miembro_id=member_id)

    def get_latest_payment(self, member_id):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            query = "SELECT [ID-Pagos], [ID-Miembros], [Fecha-Pago], [Efectivo-$], [Efectivo-Bs], [Monto-Digital-Bs], Referencia, Abono, Resto FROM Pagos WHERE [ID-Miembros] = ? ORDER BY [Fecha-Pago] DESC, [ID-Pagos] DESC"
            cursor.execute(query, (member_id,))
            columns = [column[0] for column in cursor.description]
            row = cursor.fetchone()
            if row:
                payment_dict = dict(zip(columns, row))
                referencia = payment_dict.get("Referencia", "")
                if "Tipo Membresía: Mensual" in referencia:
                    payment_dict["Tipo-Membresia"] = "Mensual"
                elif "Tipo Membresía: Quincenal" in referencia:
                    payment_dict["Tipo-Membresia"] = "Quincenal"
                else:
                    payment_dict["Tipo-Membresia"] = "Desconocido"

                return payment_dict
            return None
        except pyodbc.Error as ex:
            print(f"Error al obtener el último pago: {ex}")
            return None
        except Exception as e:
            print(f"Error inesperado en get_latest_payment: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_all_payments(self):
        """Obtiene todos los registros de pagos de la base de datos."""
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            query = "SELECT P.[ID-Pagos], P.[ID-Miembros], M.Nombre, M.Apellido, P.[Fecha-Pago], P.[Efectivo-$], P.[Efectivo-Bs], P.[Monto-Digital-Bs], P.Referencia FROM Pagos AS P INNER JOIN Miembros AS M ON P.[ID-Miembros] = M.[ID-Miembro] ORDER BY P.[Fecha-Pago] DESC"
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            payments = []
            for row in cursor.fetchall():
                payments.append(dict(zip(columns, row)))
            return payments
        except pyodbc.Error as ex:
            print(f"Error al obtener todos los pagos: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # --- Funciones específicas para Observaciones ---

    def get_observations(self, miembro_id=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            if miembro_id:
                query = "SELECT [ID-Observac], [ID-Miembro], Observacion, [Fecha de nacimiento] FROM Observaciones WHERE [ID-Miembro] = ? ORDER BY [ID-Observac] DESC"
                cursor.execute(query, (miembro_id,))
            else:
                query = "SELECT [ID-Observac], [ID-Miembro], Observacion, [Fecha de nacimiento] FROM Observaciones ORDER BY [ID-Observac] DESC"
                cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except pyodbc.Error as ex:
            print(f"Error al obtener observaciones: {ex}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # --- Funciones para Pago-Mensual y Pago-Quincenal (asumiendo que son tablas de registro de pagos específicos) ---
    def add_monthly_payment(self, miembro_id, fecha_inicio, fecha_fin):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [Pago-Mensual] WHERE [ID-Miembro] = ?", (miembro_id,))
            query = "INSERT INTO [Pago-Mensual] ([ID-Miembro], Desde, Hasta) VALUES (?, ?, ?)"
            cursor.execute(query, (miembro_id, fecha_inicio, fecha_fin))
            conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al añadir pago mensual: {ex}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_monthly_payments(self, miembro_id=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            if miembro_id:
                query = "SELECT [ID-Miembro], Desde, Hasta FROM [Pago-Mensual] WHERE [ID-Miembro] = ?"
                cursor.execute(query, (miembro_id,))
            else:
                query = "SELECT [ID-Miembro], Desde, Hasta FROM [Pago-Mensual]"
                cursor.execute(query)
            
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except pyodbc.Error as ex:
            print(f"Error al obtener pagos mensuales: {ex}")
            return []
        except Exception as e:
            print(f"Error inesperado en get_monthly_payments: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def add_fortnightly_payment(self, miembro_id, fecha_inicio, fecha_fin):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [Pago-Quincenal] WHERE [ID-Miembro] = ?", (miembro_id,))
            query = "INSERT INTO [Pago-Quincenal] ([ID-Miembro], Desde, Hasta) VALUES (?, ?, ?)"
            cursor.execute(query, (miembro_id, fecha_inicio, fecha_fin))
            conn.commit()
            return True
        except pyodbc.Error as ex:
            print(f"Error al añadir pago quincenal: {ex}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_fortnightly_payments(self, miembro_id=None):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            if miembro_id:
                query = "SELECT [ID-Miembro], Desde, Hasta FROM [Pago-Quincenal] WHERE [ID-Miembro] = ?"
                cursor.execute(query, (miembro_id,))
            else:
                query = "SELECT [ID-Miembro], Desde, Hasta FROM [Pago-Quincenal]"
                cursor.execute(query)
            
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except pyodbc.Error as ex:
            print(f"Error al obtener pagos quincenales: {ex}")
            return []
        except Exception as e:
            print(f"Error inesperado en get_fortnightly_payments: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_member(self, member_id):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Asistencia WHERE [ID-Miembro] = ?", (member_id,))
            cursor.execute("DELETE FROM Pagos WHERE [ID-Miembros] = ?", (member_id,))
            cursor.execute("DELETE FROM Observaciones WHERE [ID-Miembro] = ?", (member_id,))
            cursor.execute("DELETE FROM [Pago-Mensual] WHERE [ID-Miembro] = ?", (member_id,))
            cursor.execute("DELETE FROM [Pago-Quincenal] WHERE [ID-Miembro] = ?", (member_id,))
            
            query = "DELETE FROM Miembros WHERE [ID-Miembro] = ?"
            cursor.execute(query, (member_id,))
            conn.commit()
            print(f"Miembro ID {member_id} y sus registros asociados eliminados exitosamente.")
            return True
        except pyodbc.Error as ex:
            print(f"Error al eliminar miembro: {ex}")
            return False
        except Exception as e:
            print(f"Error inesperado al eliminar miembro: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def create_fortnightly_payment_table(self):
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT 1 FROM [Pago-Quincenal] WHERE 1=0")
                print("La tabla Pago-Quincenal ya existe.")
                return
            except pyodbc.ProgrammingError:
                pass
            except Exception as e:
                print(f"Error inesperado al verificar la existencia de la tabla Pago-Quincenal: {e}")
                return

            query = """
            CREATE TABLE [Pago-Quincenal] (
                [ID-Miembro] LONG,
                Desde DATE,
                Hasta DATE
            )
            """
            cursor.execute(query)
            conn.commit()
            print("Tabla Pago-Quincenal creada exitosamente.")
        except pyodbc.Error as ex:
            print(f"Error al crear la tabla Pago-Quincenal: {ex}")
        except Exception as e:
            print(f"Error inesperado al crear la tabla Pago-Quincenal: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
