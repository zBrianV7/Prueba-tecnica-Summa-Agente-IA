import pandas as pd
import sqlite3
import re
import os

class Database:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"No se encontró el archivo en: {self.excel_path}")
            
        df = pd.read_excel(self.excel_path)
        
        # 1. Normalizar nombres de columnas
        df.columns = [c.replace(' ', '_').lower() for c in df.columns]
        
        # 2. Limpieza de dinero (buscamos 'censatias' o 'cesantias')
        col_money = [c for c in df.columns if 'cesan' in c or 'censan' in c]
        if col_money:
            target = col_money[0]
            df[target] = df[target].astype(str)
            df[target] = df[target].str.replace('$', '', regex=False).str.strip()
            df[target] = df[target].str.replace('.', '', regex=False)
            df[target] = df[target].str.replace(',', '.', regex=False)
            df[target] = pd.to_numeric(df[target], errors='coerce').fillna(0)
            df = df.rename(columns={target: 'cesantias'})

        # 3. Cargar a la base de datos
        df.to_sql('cesantias', self.conn, index=False, if_exists='replace')
        print(f"Datos cargados. Columnas: {list(df.columns)}")

    def query(self, sql_query):
        forbidden_keywords = ["drop", "delete", "insert", "update", "alter", "truncate", "create"]
        clean_query = sql_query.lower().strip()
        
        if any(word in clean_query for word in forbidden_keywords):
            return "ERROR DE SEGURIDAD: Solo lectura permitida."

        if not clean_query.startswith("select"):
            return "ERROR: Solo consultas SELECT."

        try:
            if "limit" not in clean_query:
                clean_query += " LIMIT 10"
            return pd.read_sql_query(clean_query, self.conn).to_dict(orient='records')
        except Exception as e:
            return f"Error en la ejecución: {str(e)}"

    def get_schema(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(cesantias)")
        cols = [f"{row[1]} ({row[2]})" for row in cursor.fetchall()]
        return f"Tabla: cesantias | Columnas: {', '.join(cols)}"