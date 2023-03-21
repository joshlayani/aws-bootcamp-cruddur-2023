# Week 1 — App Containerization

Here is the homework I completed:
- Watched all week 1 videos (live stream, supplemental content, security considerations, etc.)
- Installed and set up docker and signed up for docker hub
- Added documentation to the notifications endpoint in OpenAPI yml file
- Added the flask backend notifications endpoint
- Added the frontend notifications page
- Added dynamoDB Local and Postgres to docker-compose and ensured that the containers were working properly
- Researched best practices for Dockerfiles
- Installed docker on my local machine and got containers running in my local vscode

&nbsp;

# Workspace Updates

## Update `.gitpod.yml`:

Add the following code to the `.gitpod.yml` file to install postgres automatically on workspace launch.

```yml
- name: postgres
    init: |
      curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
      echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
      sudo apt update
      sudo apt install -y postgresql-client-13 libpq-dev
```

&nbsp;

# Docker

## Create `frontend-react-js/Dockerfile`:

The following code loads the node.js image, runs npm install, and starts the frontend of the app. Add it to `frontend-react-js/Dockerfile`.

```Dockerfile
FROM node:16.18

ENV PORT=3000

COPY . /frontend-react-js
WORKDIR /frontend-react-js
RUN npm install
EXPOSE ${PORT}
CMD ["npm", "start"]
```

## Create `backend-flask/Dockerfile`:

The following code uses the official Python image as the base image, initializes the working directory as backend-flask, exposes the port the app will run on, and starts the flask application. Add it to `backend-flask/Dockerfile`.

```dockerfile
FROM python:3.10-slim-buster

WORKDIR /backend-flask

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_ENV=development

EXPOSE ${PORT}
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
```

## Create `docker-compose.yml`:

Docker Compose simplifies the process of managing and orchestrating Docker containers, networks, and volumes. This makes it easier to maintain and deploy complex applications. 

Each service defined below will run its own container. We've added a container for the frontend, the backend, dynamodb-local, and our postgres database.

```yml
version: "3.8"
services:
  backend-flask:
    environment:
      FRONTEND_URL: "https://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./backend-flask
    ports:
      - "4567:4567"
    volumes:
      - ./backend-flask:/backend-flask
  frontend-react-js:
    environment:
      REACT_APP_BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./frontend-react-js
    ports:
      - "3000:3000"
    volumes:
      - ./frontend-react-js:/frontend-react-js
  dynamodb-local:
    user: root
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ./data"
    image: "amazon/dynamodb-local:latest"
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal
  db:
    image: postgres:13-alpine
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - '5432:5432'
    volumes: 
      - db:/var/lib/postgresql/data

networks: 
  internal-network:
    driver: bridge
    name: cruddur

volumes:
  db:
    driver: local
```

## Dockerfile best practices:

- Build ephemeral containers. This means that the containers may be destroyed and rebuilt easily.
- Exclude irrelevant files using a .dockerignore file. This works in the same way as the .gitignore file.
- Use multistage builds. This allows a reduction in stage of the final image by leveraging the build cache.
- Avoid installing unneccessary packages. This one speaks for itself, only install necessary packages.
- Decouple applications. One container, one purpose. This is done so that it is easier to scale the application horizontally.
- Minimize the number of layers. 'RUN' 'COPY' and 'ADD' create layers, other commands don't increase the size of the image.

&nbsp;

# Notifications

## Update `backend-flask/openapi-3.0.yml`:

First, lets add the notifications endpoint to `backend-flask/openapi-3.0.yml`.

```yml
/api/activities/notifications:
  get:
    description: Return a feed of activity for all my following
    tags:
      - activities
    parameters: []
    responses:
      '200':
        description: Returns an array of activities
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Activity'
```


## Create `backend-flask/services/notifications_activities.py`:

Next, let's add the following NotificationsActivities class to `backend-flask/services/notifications_activities.py`. The run method will return mock data until we connect it to the database.

```python
from datetime import datetime, timedelta, timezone
class NotificationsActivities:
  def run():
    now = datetime.now(timezone.utc).astimezone()
    results = [{
      'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
      'handle':  'Wayne',
      'message': 'suh dude',
      'created_at': (now - timedelta(days=2)).isoformat(),
      'expires_at': (now + timedelta(days=5)).isoformat(),
      'likes_count': 5,
      'replies_count': 1,
      'reposts_count': 0,
      'replies': [{
        'uuid': '26e12864-1c26-5c3a-9658-97a10f8fea67',
        'reply_to_activity_uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
        'handle':  'Worf',
        'message': 'This post has no honor!',
        'likes_count': 0,
        'replies_count': 0,
        'reposts_count': 0,
        'created_at': (now - timedelta(days=2)).isoformat()
      }],
    }
    ]
    return results
```

## Update `backend-flask/app.py`:

We can now import the NotificationsActivities class into `backend-flask/app.py`.

```python
from services.notifications_activities import *
```

Next we can add our api route to `backend-flask/app.py`. This method will call the run method we created in NotificationsActivities. 

```python
@app.route("/api/activities/notifications", methods=['GET'])
def data_notifications():
  data = NotificationsActivities.run()
  return data, 200
```

## Create `frontend-react-js/src/pages/NotificationsFeedPage.css`:

Leave this file blank for now, we'll add custom CSS to it when necessary.

## Create `frontend-react-js/src/pages/NotificationsFeedPage.js`:

Add the following Javascript code to this file. This calls the notifications API endpoint and returns it in the feed.

```javascript
import './NotificationsFeedPage.css';
import React from "react";

import DesktopNavigation  from '../components/DesktopNavigation';
import DesktopSidebar     from '../components/DesktopSidebar';
import ActivityFeed from '../components/ActivityFeed';
import ActivityForm from '../components/ActivityForm';
import ReplyForm from '../components/ReplyForm';

// [TODO] Authenication
import Cookies from 'js-cookie'

export default function NotificationsFeedPage() {
  const [activities, setActivities] = React.useState([]);
  const [popped, setPopped] = React.useState(false);
  const [poppedReply, setPoppedReply] = React.useState(false);
  const [replyActivity, setReplyActivity] = React.useState({});
  const [user, setUser] = React.useState(null);
  const dataFetchedRef = React.useRef(false);

  const loadData = async () => {
    try {
      const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/activities/notifications`
      const res = await fetch(backend_url, {
        method: "GET"
      });
      let resJson = await res.json();
      if (res.status === 200) {
        setActivities(resJson)
      } else {
        console.log(res)
      }
    } catch (err) {
      console.log(err);
    }
  };

  const checkAuth = async () => {
    console.log('checkAuth')
    // [TODO] Authenication
    if (Cookies.get('user.logged_in')) {
      setUser({
        display_name: Cookies.get('user.name'),
        handle: Cookies.get('user.username')
      })
    }
  };

  React.useEffect(()=>{
    //prevents double call
    if (dataFetchedRef.current) return;
    dataFetchedRef.current = true;

    loadData();
    checkAuth();
  }, [])

  return (
    <article>
      <DesktopNavigation user={user} active={'notifications'} setPopped={setPopped} />
      <div className='content'>
        <ActivityForm  
          popped={popped}
          setPopped={setPopped} 
          setActivities={setActivities} 
        />
        <ReplyForm 
          activity={replyActivity} 
          popped={poppedReply} 
          setPopped={setPoppedReply} 
          setActivities={setActivities} 
          activities={activities} 
        />
        <ActivityFeed 
          title="Notifications" 
          setReplyActivity={setReplyActivity} 
          setPopped={setPoppedReply} 
          activities={activities} 
        />
      </div>
      <DesktopSidebar user={user} />
    </article>
  );
}
```

## Update `frontend-react-js/src/App.js`:

Finally we can import the NotificationsFeedPage into our App.js file.

```javascript
import NotificationsFeedPage from './pages/NotificationsFeedPage';
```

And add the following code to the router.

```javascript
{
    path: "/notifications",
    element: <NotificationsFeedPage />
},
```