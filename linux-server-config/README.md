# udacity-linux-server-configuration
This repo contains a README which lists the commands/procedures needed to fulfill the requirements of Udacity's Linux Server Configuration project. The purpose of this project is to set up a Linux server to host a Flask web application.

## Create a new user named grader
User was graded using `useradd grader`. Password was set using `passwd grader`. To create SSH keys that will be used for authentication, I used `ssh-keygen` as that user.
## Give the grader the permission to sudo
`visudo` allows you to edit the /etc/sudoers file. The following was added: 
>grader  ALL=(ALL) NOPASSWD: ALL

## Update all currently installed packages
`apt update` to update the metadata, `apt upgrade` to perform the updates, `reboot` to apply kernel changes
##Change the SSH port from 22 to 2200
Edit /etc/ssh/sshd_config 
>Port 2200

## Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)
`ufw allow 2200; ufw allow 123; ufw allow 80`
## Configure the local timezone to UTC
`dpkg-reconfigure tzdata` and select UTC
## Install and configure Apache to serve a Python mod_wsgi application
`apt install apache2 libapache2-mod-wsgi`
## Install and configure PostgreSQL:
`apt install postgresql`. 
## Do not allow remote connections
Postgres is listening only on localhost by default.
### Create a new user named catalog that has limited permissions to your catalog application database

    Switch to the postgres user with `su - postgres` then run `psql`. 
    Add the user with `create user catalog with password 'Add the database with '5PUURTKV5Wsr';`. 
    Create the database with `create database catalog;` then give permissions to the user `grant all privileges on database catalog to catalog;`.
    
## Install git, clone and setup your Catalog App project (from your GitHub repository from earlier in the Nanodegree program) so that it functions correctly when visiting your server’s IP address in a browser. Remember to set this up appropriately so that your .git directory is not publicly accessible via a browser! 

[Help from DigitalOcean](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=4&cad=rja&uact=8&ved=0ahUKEwiSzoXevvTRAhVKOSYKHXcvAskQFggyMAM&url=https%3A%2F%2Fwww.digitalocean.com%2Fcommunity%2Ftutorials%2Fhow-to-deploy-a-flask-application-on-an-ubuntu-vps&usg=AFQjCNGutS1Ufl5TuhsY-RAUJrPmerKpMA&sig2=xQkvf4FmGEU9s0BibSVyCQ)
Created an apache config file for the site that looks like:

    <VirtualHost *:80>
        ServerName 52.24.183.0
        ServerAlias ec2-52-24-183-0.us-west-2.compute.amazonaws.com
        ServerAdmin webmaster@localhost
        WSGIScriptAlias / /var/www/catalog/flaskapp.wsgi
        <Directory /var/www/catalog/catalog/>
            Order allow,deny
            Allow from all
        </Directory>
        Alias /static /var/www/catalog/catalog/static
        <Directory /var/www/catalog/catalog/static/>
            Order allow,deny
            Allow from all
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>

Clone the project:
`cd /var/www; git clone git@github.com:kimobu/fullstack-item-catalog.git`. Renamed the fullstack-item-catalog directory to catalog, then moved the catalog directory from catalog/vagrant up a directory. Within /var/www/catalog, created a config file for WSGI:

    #!/usr/bin/python
    import sys
    sys.path.insert(0,"/var/www/catalog/")
    
    from catalog import app as application
    application.secret_key = '3GblcjPrbpQzo8jYOKRj'
    
Had to install pip by downloading and running get_pip.py, then installed dependencies for the application:

    pip install flask
    pip install sqlalchemy
    apt install postgresql-server-dev-9.3
    pip install psycopg2
    pip install oauth2client


Finally, edited /etc/ssh/sshd_config again to disallow root login by setting
> PermitRootLogin no

