# ip-reputation-api

This application is an ip-reputation microservice written using FastAPI and sqlite. 

Inspired by recent security classes and a recommendation from a former interviewer and friend, this project is my way of learning how to build and deploy a microservice. Keep in mind I still am a student, so this is not a perfect product. I am open to any suggestions people might have as I am still learning.

The application is meant to be highly customizable. You can easily choose which IP lists to include using the `update-ipsets` script and by modifying the Dockerfile. The database can be populated with data from up to 600 million potentially malicious IPs, sourced from various vendors and maintained by FireHOL.

### Installation 
To run this, you must have Docker Desktop installed. 

To get started, simply clone the repository and run the following commands:

`docker compose build`

and

`docker compose up` 

If you just want the image or if you would like to customize and mess around, you can first build it and then run an interactive shell. 

`docker build -t ipsecapi:latest .`

If it built correctly, you should be able to view it by running 

`docker images`

![image](https://github.com/user-attachments/assets/30757d94-1fe9-4c65-93c7-1f5c782b6159)

after confirming it built correctly, run an interactive shell using

`docker run -it -rm ipsecapi:latest /bin/bash`

This should open up a shell as root on the container you can play around with. 

![image](https://github.com/user-attachments/assets/646da52e-83f3-4778-967e-3a449460b348)

You can run the `update-ipsets` script which should tell you which lists are currently enabled. 

To enable a new list, run `update-ipsets enable [list name]`.

To disable a list, navigate to `/etc/firehol/ipsets` and delete the `.source` file of the list you no longer want included. 

This installs FireHOL and the `update-ipsets` script as well as two services: 

1. The `update-ipsets` script which allows selection of which lists to include for the API. More information can be found on how to use this script [here](https://github.com/firehol/blocklist-ipsets/wiki).

The services include: 

1. a cron job that pulls information from your selected sources using `update-ipsets` and populates a database.
2. an API service that will match malicious IPs to your selected sources. 

### cron job 
This pulls information from FireHOL periodically and updates an sqlite3 database that the API is connected to. 

### API Service 
This is something you can deploy via AWS ECS and query to see if an IP matches a malicious IP from one of the vendors using the `blacklist` endpoint. 

![image](https://github.com/user-attachments/assets/e7eeb2b1-5664-466d-ae73-c94600fbe5d0)

Each vendor, represented using a `list_id` also has information via the API that can be queried using the `providers` endpoint.

![image](https://github.com/user-attachments/assets/f81ae67c-ac6f-43bf-af3b-e49e12933330)

Currently there are still some additional features in development and testing to be done. 

Special thanks to Andrew Katz and Jose Haro Peralta for helping me with this project. 



