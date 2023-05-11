from psycopg_pool import ConnectionPool
import os, sys, re
from flask import current_app as app

class DB:
  def __init__(self):
    self.init_pool()

  def init_pool(self):
    connection_url = os.getenv("CONNECTION_URL")
    self.pool = ConnectionPool(connection_url)

  def query_commit(self, sql, params={}): #commits data (i.e. insert)

    self.print_sql('commit w return', sql)

    pattern = r"\bRETURNING\b"
    is_returning_id = re.search(pattern, sql)
    try:
      with self.pool.connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params) 
        conn.commit()
        if is_returning_id:
          return cur.fetchone()[0]
    except Exception as err:
      self.print_sql_err(err)

  def print_sql_err(self,err):
    err_type, err_obj, traceback = sys.exc_info()
    line_num = traceback.tb_lineno
    print ("\npsycopg ERROR:", err, "on line number:", line_num)
    print ("psycopg traceback:", traceback, "-- type:", err_type)
    print ("pgerror:", err.pgerror)
    print ("pgcode:", err.pgcode, "\n")

  def query_wrap_object(self, template):
    sql = f"""
    (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
    {template}
    ) object_row);
    """
    return sql

  def query_wrap_array(self, template):
    sql = f"""
    (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
    {template}
    ) array_row);
    """
    return sql

  def query_object_json(self, sql, params={}): #returns json object
    self.print_sql('object', sql)
    wrapped_sql = self.query_wrap_object(sql)
    with self.pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(wrapped_sql, params)
          json = cur.fetchone()
          return json[0]


  def query_array_json(self, sql, params={}): #returns array of json objects
    self.print_sql('array', sql)
    wrapped_sql = self.query_wrap_array(sql)
    with self.pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(wrapped_sql, params)
          json = cur.fetchone()
    return json[0]

  def template(self, *args):
    pathing = list((app.root_path,'db','sql') + args)
    pathing[-1] = pathing[-1] + '.sql'

    template_path = os.path.join(*pathing)

    green = '\033[92m'
    no_color = '\033[0m'
    print(f'{green} Loading SQL Template ---- {template_path} {no_color}')

    with open(template_path, 'r') as f:
      template_content = f.read()
    return template_content

  def query_value(self,sql,params={}):
    self.print_sql('value',sql,params)

    with self.pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(sql,params)
        json = cur.fetchone()
        return json[0]

  def print_sql(self, title, sql, params={}):
    cyan = '\033[96m'
    no_color = '\033[0m'
    print(f'{cyan}SQL ---- {title}{no_color}')
    print(sql, params)

db = DB()