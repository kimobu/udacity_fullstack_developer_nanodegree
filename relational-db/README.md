# Swiss Pairings tournament
This repository implements the Udacity Full Stack Nanodegree project
requirements for the Relational Databases module. It provides
[Swiss pairings](https://en.wikipedia.org/wiki/Swiss-system_tournament)

# Usage
This project assumes a Postgres backend that is included with the Vagrant VM.

To setup vagrant:

`cd vagrant; vagrant up; vagrant ssh`

Note: MacOS users may need to follow the workaround for curl found [here](https://github.com/mitchellh/vagrant/issues/7997)

To setup the database, perform the following from within the Vagrant shell:

`psql -f tournament.sql`

To test the application, perform from within the Vagrant shell:

`python tournament_test.py`

# Files
## tournament.sql
This file contains SQL commands to create the database, tables, and views needed by the application.

## tournament.py
This is a python program with functions to interact with the database. This allows someone to insert and delete players and matches, and to query standings and pairings.

## tournament_test.py
This is a python program to perform unit tests
