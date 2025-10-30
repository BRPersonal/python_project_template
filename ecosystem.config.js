//This file is for deploying app to production using tool pm2
module.exports = {
  apps: [{
    name: "aiQuizBot-be",
    script: "app.py",
    cwd: __dirname,  //current working directory same as this file
    interpreter: "./.venv/bin/python",
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: "200M",
    env: {
      PYTHONUNBUFFERED: "1",  // Important for real-time logs
      ENV: "production"
    },
    error_file: "./logs/python-err.log",
    out_file: "./logs/python-out.log",
    time: true
  }]
};