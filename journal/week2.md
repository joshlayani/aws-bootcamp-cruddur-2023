# Week 2 — Distributed Tracing



&nbsp;

# Workspace Updates

## Update `.gitpod.yml`:

### Run npm i on workspace launch:
Add the following code to run npm install automatically whenever we launch gitpod.

```yml
- name: react-js
    command: |
      cd /frontend-react-js
      npm i
```

### Keep ports open:
Add the following code to run npm install automatically whenever we launch gitpod.

```yml
ports:
  - name: frontend
    port: 3000
    onOpen: open-browser
    visibility: public
  - name: backend
    port: 4567
    visibility: public
  - name: xray-daemon
    port: 2000
    visibility: public
```

&nbsp;

# Python package requirements
## Update `backend-flask/requirements.txt`:
Lets add the following python packages to `backend-flask/requirements.txt`. This adds the required packages to our project.

```
opentelemetry-api 
opentelemetry-sdk 
opentelemetry-exporter-otlp-proto-http 
opentelemetry-instrumentation-flask 
opentelemetry-instrumentation-requests

aws-xray-sdk
watchtower
```

&nbsp;

# Docker

## Update `docker-compose.yml`
Add the following environment variables to the `docker-compose.yml` file:

```yml
OTEL_SERVICE_NAME: 'backend-flask'
OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
AWS_XRAY_URL: "*4567-${GITPOD_WORKSPACE_ID}.{GITPOD_WORKSPACE_CLUSTER_HOST}"
AWS_XRAY_DAEMON_ADDRESS: "xray-daemon:2000"
AWS_DEFAULT_REGION: "${AWS_DEFAULT_REGION}"
AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
```

Next, add the xray-daemon as follows:
```yml
xray-daemon:
    image: "amazon/aws-xray-daemon"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
      AWS_REGION: "us-east-1"
    command: 
      - "xray -o -b xray-daemon:2000"
    ports:
      - 2000:2000/udp
```

&nbsp;

# Honeycomb

## Update `backend-flask/app.py`:

First add the following imports.
```python
#HONEYCOMB
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
```

Next, lets initialize the tracer.
```python
#Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)

simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(simple_processor)

trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
```

Next, we can add the following code below the `app = Flask(__name__)` line.
```python
#Honeycomb
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
```

## Update `backend-flask/services/home_activities.py`:

First, add the following import.

```python
from opentelemetry import trace
```
 Next, get the tracer.

```python
tracer = trace.get_tracer("home.activities")
```

Finally, wrap the results object in the run() method as follows:
```python
with tracer.start_as_current_span("home-activities-mock-data"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      results = [...]
      span.set_attribute("app.result_length", len(results))
```

We are now getting traces with our span data in Honeycomb whenever our home_activities gets called.

&nbsp;

# AWS Xray

## Create `aws/json/xray.json`:
Add the following json to this file.

```json
{
    "SamplingRule": {
        "RuleName": "Cruddur",
        "ResourceARN": "*",
        "Priority": 9000,
        "FixedRate": 0.1,
        "ReservoirSize": 5,
        "ServiceName": "backend-flask",
        "ServiceType": "*",
        "Host": "*",
        "HTTPMethod": "*",
        "URLPath": "*",
        "Version": 1
    }
}
```

## Update `backend-flask/app.py`:

Add the following import statements.

```python
#XRAY
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
```

Initialize Xray as follows

```python
#Xray
xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)
```

Now we can add the following code below the `app = Flask(__name__)` line.
```python
XRayMiddleware(app, xray_recorder)
```

Next, in the route for the api endpoint we wish to trace (user_activities in our case) we can add the following line above the method definition.
```
@xray_recorder.capture('user_activities')
```

## Update `backend-flask/services/user_activities.py`:

Add the following import statements.

```python
from aws_xray_sdk.core import xray_recorder
```

Next, wrap the contents of the run() method in a try block as follows:

```python
try:
    model = {
      'errors': None,
      'data': None
    }

    ...
    ...
    ...
    
    model['data'] = results

    xray
    subsegment = xray_recorder.begin_subsegment('mock-data')

    dict = {
      "now": now.isoformat(),
      "result-size": len(model['data'])
    }

    subsegment.put_metadata('key', dict, 'namespace')
    xray_recorder.end_subsegment()

finally:
    xray_recorder.end_subsegment()
```

We now have a working xray trace when calling the user activity. I ultimately decided to comment out the xray code in my project.

&nbsp;

# AWS Cloudwatch Logs

## Update `backend-flask/app.py`:

Add the following import statements.

```python
#Cloudwatch Logs
import watchtower
import logging
from time import strftime
```

Initialize the logger as follows:

```python
#CloudWatch Logs
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')
LOGGER.addHandler(console_handler)
LOGGER.addHandler(cw_handler)
```

Now we can add the following code below the `app = Flask(__name__)` line.

```python
@app.after_request
def after_request(response):
  timestamp = strftime('[%Y-%b-%d %H:%M]')
  LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.start_as_current_span)
  return response
```

Finally, we can pass our logger object to out Activities in the run() method as follows:
```python
@app.route("/api/activities/home", methods=['GET'])
def data_home():
  data = HomeActivities.run(logger=LOGGER)
  return data, 200
```

## Update `backend-flask/services/home_activities.py`:

Update the run() method to take a logger object as an argument. The logger can now be called from anywhere in that method.

```python
class HomeActivities:
  def run(logger):
    #logger.info("home_activities")
```

We can now get cloudwatch logs and debug our code more efficiently.
