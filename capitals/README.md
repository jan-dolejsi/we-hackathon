# appengine-hackathon-flask-guestbook
```
Edit the guestbook.py file and update the <YOUR PROJECT ID> with your project id
```
## setup
```
virtualenv new_venv

# windows
new_venv\scripts\activate.bat

# bash

pip install -r requirements.txt

```
## deploy
```
pip install -r requirements.txt -t lib
gcloud app deploy --project=<projectname> --version=v1 ./guestbook.yaml

#browse to
(service) https://guestbook-dot-<projectname>.appspot.com
(default) https://<projectname>.appspot.com
```
