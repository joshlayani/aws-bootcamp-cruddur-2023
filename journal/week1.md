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

### Docker installation and getting familiar
Docker was not showing up on gitpod so I had to manually install it. Ensured that I already had docker installed on my local machine, and made sure it was in a useable state. Next I got familiar with how Dockerfiles work and best practices for how they are written by taking a look at [this documentation article](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/).

I learned that each instruction in a Dockerfile essentially creates a layer. The first command is usually 'FROM' which specifies the base image on top of which we wish to build our Docker image. Then the 'COPY' command is used to add the files from my directory to the container. Next, 'RUN' will build the application and 'CMD' will specify the command to run within the container (usually the apps entry point).

### Dockerfile best practices

- Build ephemeral containers. This means that the containers may be destroyed and rebuilt easily.
- Exclude irrelevant files using a .dockerignore file. This works in the same way as the .gitignore file.
- Use multistage builds. This allows a reduction in stage of the final image by leveraging the build cache.
- Avoid installing unneccessary packages. This one speaks for itself, only install necessary packages.
- Decouple applications. One container, one purpose. This is done so that it is easier to scale the application horizontally.
- Minimize the number of layers. 'RUN' 'COPY' and 'ADD' create layers, other commands don't increase the size of the image.

### Notifications Page

Adding the notifications page was very straightforward. Following the instructions in the live stream I first documented the API adding the endpoint for notifications. Then I added the endpoint to the backend, and finally added the Notifications Page to the front end. I ensured it all worked as intended.

### DynamoDB Local

Having worked with DynamoDB Local for work, I was already fairly familiar with this part. I ran the container and ensured the aws-cli commands worked as shown in the livestream.

### Postgres

I've also used Postgres for work so I had some familiarity with the commands already. Also ensured the container ran properly and the psql command worked.
