from invoke import task, run


@task
def test():
    unittest()
    style()


@task
def style():
    run(
            'flake8 --max-line-length 9999 --ignore E128,E126,E261 --exclude "__init__.py,wsgi.py,settings.py" sana_pchr && echo flake8 OK',
            echo=True)


@task
def unittest():
    run('python manage.py test sana_pchr', echo=True, pty=True)
