# Tournament Planner

Tournament Planner is for Swiss tournament system which include prevent rematch and draw

# Quick start

* Install with Python if you don't have - We recommand you to install Python v2.7.8 becuase we have tested on this version.

* Setting up your Vagrant VM with https://www.udacity.com/wiki/ud197/install-vagrant

* Download tournament directory

* Tournament directory in the terminal, use the command **vagrant up** (powers on the virtual machine) followed by **vagrant ssh**, then **cd /vargrant/tournament**

* First, you must create database. so run **psql**

* Type **CREATE DATABASE tournament;** and enter

* Type **\c tournament;** and then you get **You are now connected to database "tournament" as user "vagrant".**

* And then, run **\i tournament.sql**.

* Exit psql **\q** or ctrl+D

* Run **python tournament_test.py**

# What's included

Within the download you'll find the following directories and files. You'll see something like this:

    movie_trailer/
        tournament_test.py
        tournament.py
        tournament.sql
        README.md
