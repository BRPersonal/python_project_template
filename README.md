# python_project_template
Basic python project using FastAPI showing best practices

$ uv sync
$ source .venv/bin/activate
$ docker-compose up -d

$ python app.py
Browse the url
http://localhost:8002/health
http://localhost:8002/health/database

$docker-compose down -v

Securing the app with https
------------------
Install nginx
Assuming you have got a domain name as humble.simple.in
mapped to your server and your app is running in port 8002

sudo vi /etc/nginx/sites-available/humble.simple.in
server {
    listen 80;
    server_name humble.simple.in;

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

sudo ln -s /etc/nginx/sites-available/humble.simple.in /etc/nginx/sites-enabled/
sudo nginx -t

sudo systemctl reload nginx

sudo certbot --nginx -d humble.simple.in

verify
https://humble.simple.in - Should work with SSL
http://humble.simple.in - Should redirect to HTTPS

check auto-renewal
sudo certbot renew --dry-run

$ echo | openssl s_client -connect humble.simple.in:443 2>/dev/null | openssl x509 -noout -dates
notBefore=Oct 16 08:05:48 2025 GMT
notAfter=Jan 14 08:05:47 2026 GMT


Deployment
-----------
$ pm2 start ecosystem.config.js  (for the first time)

verify app is running
$ lsof -i:8002

susbsequent times
$ pm2 start python-template-project
$ pm2 stop python-template-project
$ pm2 logs python-template-project

To install pm2, you should have node installed first
Install pm2 globally
npm install -g pm2
configure ecosystem.config.js. This file is for deploying app to 
production using tool pm2

pm2 automatically restarts the process if it is down.
To start automatically after reboots, you need to run
$ pm2 save

This writes the list of running apps for restoration after reboot.
Run pm2 startup
This prints a command (with your user and OS) to register PM2 with your system's 
init system (systemd, upstart, etc.).

Copy the command and execute it
Now After a reboot, PM2 should restore your apps automatically.

In linode the command usually is
systemctl enable pm2-root

Debugging
----------
get into container's mongo shell
$ docker exec -it python-template-mongodb mongosh -u admin -p password123 --authenticationDatabase admin template_db

get into container's postgre shell
$ docker exec -it python-template-postgresql psql -U postgres -d security_db

Adding Jwt based security to FastApi apps
------------
# encode jwt secret key
echo "my_secert_key_123" | base64
bXlfc2VjZXJ0X2tleV8xMjMK

--Postgre script
CREATE TABLE app_user(
    user_id BIGSERIAL NOT NULL,
    first_name VARCHAR(201) NOT NULL,
    last_name VARCHAR(201) NOT NULL,
    email_id VARCHAR(201) NOT NULL,
    password VARCHAR(1000) NOT NULL,
    roles VARCHAR(500) DEFAULT ' ',
    permissions VARCHAR(500) DEFAULT ' ',
    social_login_ids VARCHAR(1000) DEFAULT ' ',
    created_by VARCHAR(100),
    created_on TIMESTAMP,
    last_updated_by VARCHAR(100),
    last_updated_on TIMESTAMP,
    PRIMARY KEY (user_id),
    CONSTRAINT app_user_emailid_uk UNIQUE (email_id)
);

-- Add table and column comments
COMMENT ON TABLE app_user IS 'maintains user accounts';
COMMENT ON COLUMN app_user.user_id IS 'Running sequence number';
COMMENT ON COLUMN app_user.email_id IS 'User email address - must be unique';
COMMENT ON COLUMN app_user.social_login_ids IS 'comma separated unique social ids. Used to map social id to app user id';
COMMENT ON COLUMN app_user.roles IS 'User roles (e.g., admin, user, moderator)';
COMMENT ON COLUMN app_user.permissions IS 'User permissions (e.g, create,read,update,delete)';

security_db=# \d app_user
security_db=# select count('x') from app_user;
1
security_db=# select user_id,email_id,password from app_user;
 user_id |     email_id     |                           password                           
---------+------------------+--------------------------------------------------------------
       2 | demo11@email.com | $2b$12$mB/eP4LWvlgAOsf5yGo2N.JvkobJDrfgq5XqLnCKlnyt3lsEzwfHe

security_db=# delete from app_user where email_id = 'test+5.user@example.com';
security_db=# \q