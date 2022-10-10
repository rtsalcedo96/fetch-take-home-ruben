# Fetch Rewards - Ruben T. Salcedo #
## Data Engineering Take Home: ETL off a SQS Qeueue ##

The language that I have used to perform this project was Python3 using VS Code as my IDE in addition to the project setup resources.

## Project set-up troubleshooting write-up (Windows10-OS)
My journey started with trying to run the docker container but I was almost immediately blocked because the docker logs were saying that I was running into some issues regarding an ./r command and I realized the docker container was not able to execute the script command on initialization. When I ran the awslocal test command included in the project setup instructions, the terminal was responding that a queue did not exist, when I knew for a fact and could prove visually that that container was up and running in docker desktop. My belief that the container was empty was reinforced when I ran “awslocal sqs list-queues” and nothing came back.

Upon troubleshooting several different potential problems, one of the problems was the docker volumes were not being properly mounted because the $PWD variable was not being set correctly, despite it being defined on my local machine. I resolved this by ensuring the absolute file paths were copied  and pasted to my local docker-compose.yml that I pulled from my forked Fetch repo.

When I would try to execute “make start”, the conditionals in the script above the manual docker-compose commands  would result in an error/failed response in my VS code terminal. I edited the Makefile by removing the conditionals which seemingly allowed me to run “make start” without any resulting errors.

In the docker logs, I saw an error at the end showing that the “create-and-run” script was terminating early because of a /r command not found error. After researching google, I determined that this is an error that is seen when running a script in UNIX that was saved or edited on Windows. After some more research, I found that the Notepad++ software allowed me to convert the end of line (EOL) to UNIX. By converting this EOL to UNIX, it allowed the script to be run fully and properly resulting in no /r command error, thus allowing the sqs queue to be created and tested properly when calling a receive message command.

## Post-Project Reflection
With more time for this project, I would seek to optimize my code in such a way where I can reduce run time for my record insertion by pulling more messages at once from the SQS queue and iterating over them faster in my for loop. I could do this by maxing out the messages pulled from the SQS queue at once or I might be able to do this by editing my postgres query and record insertion code block to upload multiple records at once for the associate fields. This would be particularly impactful to an organization which seeks to ETL bulk loads of a vast amount of data while maintaining system integrity.

Additionally, I would seek to include documentation for steps towards daily table maintenance as well as daily monitoring of the ETL pipeline using diagnostic queries. This would ensure there are protocols in place to mitigate table degradation from data updates/deletes and resolve errors that may arise during long term use.

Note the target table's DDL is:

```sql
-- Creation of user_logins table

CREATE TABLE IF NOT EXISTS user_logins(
    user_id             varchar(128),
    device_type         varchar(32),
    masked_ip           varchar(256),
    masked_device_id    varchar(256),
    locale              varchar(32),
    app_version         varchar(15),
    create_date         date
);
```

You will have to make a number of decisions as you develop this solution:

*    How will you read messages from the queue?
*    What type of data structures should be used?
*    How will you mask the PII data so that duplicate values can be identified?
*    What will be your strategy for connecting and writing to Postgres?
*    Where and how will your application run?

**The recommended time to spend on this take home is 2-3 hours.** Make use of code stubs, doc strings, and a next steps section in your README to elaborate on ways that you would continue fleshing out this project if you had the time. For this assignment an ounce of communication and organization is worth a pound of execution.

## Project Setup
1. Fork this repository to a personal Github, GitLab, Bitbucket, etc... account. We will not accept PRs to this project.
2. You will need the following installed on your local machine
    * make
        * Ubuntu -- `apt-get -y install make`
        * Windows -- `choco install make`
        * Mac -- `brew install make`
    * python3 -- [python install guide](https://www.python.org/downloads/)
    * pip3 -- `python -m ensurepip --upgrade` or run `make pip-install` in the project root
    * awslocal -- `pip install awscli-local`  or run `make pip install` in the project root
    * docker -- [docker install guide](https://docs.docker.com/get-docker/)
    * docker-compose -- [docker-compose install guide]()
3. Run `make start` to execute the docker-compose file in the the project (see scripts/ and data/ directories to see what's going on, if you're curious)
    * An AWS SQS Queue is created
    * A script is run to write 100 JSON records to the queue
    * A Postgres database will be stood up
    * A user_logins table will be created in the public schema
4. Test local access
    * Read a message from the queue using awslocal, `awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue`
    * Connect to the Postgres database, verify the table is created
    * username = `postgres`
    * database = `postgres`
    * password = `postgres`


** NOTE: If you have a localhost software already mapped to the 5432 port, you may need to change port mappings to account for this! In my case PgAdmin4 was conflicting with my project localhost 5432 connection, so I changed my mapping to 54321:5432**

```bash
# password: postgres

psql -d postgres -U postgres  -p 5432 -h localhost -W
Password: 

postgres=# select * from user_logins;
 user_id | device_type | hashed_ip | hashed_device_id | locale | app_version | create_date 
---------+-------------+-----------+------------------+--------+-------------+-------------
(0 rows)
```
5. Run `make stop` to terminate the docker containers and optionally run `make clean` to clean up docker resources.
