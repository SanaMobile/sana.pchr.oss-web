sana.pchr-web
=============

Web applications and server configs/scripts for Lebanon PCHR project.

[![Circle CI](https://circleci.com/gh/SanaMobile/sana.pchr-web.svg?style=svg&circle-token=f55ddd352bf418c61b8dbec1964e299e9ef0a553)](https://circleci.com/gh/SanaMobile/sana.pchr-web)

Running Locally
---------------

You'll need Python 3, pip, and virtualenv installed first. Note: Your 
Python 3 should installation must have the header files-i.e. install
```python3-dev``` or similar package on Linux systems. 

    virtualenv -p python3 env
    source env/bin/activate
    pip install -r requirements_dev.txt
    python manage.py syncdb

You'll be prompted to create a superuser account when running `python manage.py syncdb` - it can be used on the [admin interface](http://localhost:8000/admin).

Then, to run the server:

    python manage.py runserver

Or the tests:

    invoke tests
