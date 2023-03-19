from datetime import datetime, timedelta, timezone
from opentelemetry import trace
from lib.db import DB


tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(cognito_user_id=None):
    #logger.info("HomeActivities")
    with tracer.start_as_current_span("home-activites-mock-data"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      
      sql = DB().template('activities', 'home')
      results = DB().query_array_json(sql)

      return results