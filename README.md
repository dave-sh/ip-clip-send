# ip-reputation-api

This application is an ip-reputation microservice written using FastAPI and sqlite. 

Inspired by recent security classes and a recommendation from a former interviewer and friend, this project is my way of learning how to build and deploy a microservice. Keep in mind I still am a student, so this is not a perfect product. I am open to any suggestions people might have as I am still learning.

The application is highly customizable. You can easily integrate your own lists using the `update-ipsets` script and by modifying the Dockerfile. The database can be populated with data from up to 600 million potentially malicious IPs, sourced from various vendors and maintained by FireHOL.

### Installation 

To get started, simply clone the repository and run the following commands:

`docker compose build`

and

`docker compose up` 

This starts two services: 

1. a cron job that pulls information from your selected sources and populates a database.
2. an API service

### cron job 
This pulls information from FireHoL.

### API Service 
This is something you can deploy via AWS ECS and query to see if an IP matches a malicious IP from one of the vendors using the `blacklist` endpoint. 

![image](https://github.com/user-attachments/assets/e7eeb2b1-5664-466d-ae73-c94600fbe5d0)

Each vendor, represented using a `list_id` also has information via the API that can be queried using the `providers` endpoint.

![image](https://github.com/user-attachments/assets/f81ae67c-ac6f-43bf-af3b-e49e12933330)

Currently there are still some additional features in development and testing to be done. 

Special thanks to Andrew Katz and Jose Haro Peralta for helping me with this project. 



