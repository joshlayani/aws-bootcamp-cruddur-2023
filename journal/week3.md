# Week 3 — Decentralized Authentication

Week 3 was about using Cognito to handle the authentication for the website. Before getting started with the live stream I watched Ashish's Decentralized Authentication security considerations video and did the quiz. 

## Setting up Cognito in the frontend

In the live stream we first set up our Cognito User Pool and implemented our sign in page. While doing that I ran into a few issues with the user pool but eventually got them resolved relatively easily. Next, we implemented the signup, confirmation, and recovery pages for the website. On each page I had to replace the use of cookies with a use of the Cognito service. Those tasks were relatively simple and I was able to get by without too many problems.

## Setting up Cognito in the backend

In the JWT token video we implemented the authentication verification in the backend. This took a lot more googling than for setting up the front end. I also used chatgpt to get a better understanding of how JWT tokens are verified on the server side.

## Improving CSS with Theme Variables

Finally, I added variables for common colors that are being reused throughout our app's css. More work needs to be done on this.