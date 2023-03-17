# Week 2 — Distributed Tracing

Week 2 was all about tracing and logging. We implemented a number of different tools to get some more visibility into our code. But I ultimately ended up making some choices for the application.

### Honeycomb
In the livestream we explored how to use and implement honeycomb. I followed the instructions and successfully got traces for the application in the home_activities.

### AWS Xray
Xray was a little bit more complicated to implement. I ran into issues while trying to implement subsegements but ended up figuring it out thanks to the follow up video. 

### AWS Cloudwatch Logs
Cloudwatch logs are essential for me when developing. It is much easier to debug issues with cloudwatch logs. Cloudwatch is simple to set up and very easy to implement.


## Conclusion
For this application I am choosing to implement Honeycomb.io and Cloudwatch logs to get more visibility into my code.