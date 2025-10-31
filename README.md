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
$ pm2 restart python-template-project
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
$ docker exec -it python-template-mongodb mongosh -u admin -p password123 --authenticationDatabase admin ai_quiz_bot
