# ip-reputation-api

This application is an ip-reputation microservice written using FastAPI and sqlite. 

I recently after taking some security classes became interested in writing a software application with a security purpose. This project was inspired by a former interviewer and good friend and I thought it would be a
great opportunity to get my hands dirty with microservices. 

I set it up to be very customizable so you can add in your own lists using the update-ipsets script and by modifying the Dockerfile. The data is pulled from 600 million possible malicious IPs from various vendors and is
maintained by FireHOL. 

To get started, simply clone the repository and run the following commands:

`docker compose build`

`docker compose up` 

This starts an API service from your local machine that you can also deploy and query to see if an IP matches a malicious IP from one of the vendors using the `blacklist` endpoint. 

![image](https://github.com/user-attachments/assets/e7eeb2b1-5664-466d-ae73-c94600fbe5d0)

Each vendor, represented using a `list_id` also has information via the API that can be queried using the `providers` endpoint.

![image](https://github.com/user-attachments/assets/f81ae67c-ac6f-43bf-af3b-e49e12933330)

Currently I'm making a front end that modifies the windows right click menu and will allow you to do a quick lookup from your clipboard. 



