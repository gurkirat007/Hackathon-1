# Hackathon-1
## To run the flask app on local server
### requirements:
Flask_SocketIO==5.0.1
Flask==1.1.2
sqlite3

### run application
inside the {Hackathon-1} folder on terminal
execute command "flask run"

## To deploy the flask app on Heroku
(security error coming on heroku so try using local server)
### the requirements.txt file should contain
Flask_SocketIO==5.0.1
Flask==1.1.2

### steps
1) heroku login -i
2) heroku git:remote -a {app_name}
(make sure to change the {app_name} to real app name}
3) git push heroku master

### open the link
https://{app_name}.herokuapp.com/



