# coding=utf-8

import os
import subprocess
import sys

import click

from app import create_app,db

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = create_app('development')

"""
    Set up Celery Commands
"""
@app.cli.command()
@click.argument('drop_first', nargs=-1)
def initdb(drop_first):
    """Initialize the database."""
    click.echo('Init the db')
    if drop_first:
        db.drop_all()
    db.create_all()

@app.cli.command()
def local_celery():
    """Run celery on local machine"""
    click.echo('Start Celery on Machine')
    ret = subprocess.call(
        ['celery', 'worker', '-A', 'celery_worker.celery', '--loglevel=info', '-P', 'eventlet'])
    sys.exit(ret)


@app.cli.command()
def celery():
    """ Start 2 celery daemon processes"""
    try:
        subprocess.call(
            ['celery', 'multi', 'start', '2', '-A', 'celery_worker.celery', '--loglevel=DEBUG', '--autoscale=4,1',
             '-Ofair', '--logfile=celery_logs/celery-worker-%n.log', '--pidfile=celery_logs/celery-worker-%n.pid '
                , '-P', 'eventlet'])
    except Exception as e:
        click.echo('Exception occurred. Run code locally')


@app.cli.command()
def kill_celery():
    """Kills all daemon processes"""
    try:
        subprocess.call(
            ['celery', 'multi', 'stop', '2', '-A', 'celery_worker.celery', '--logfile=celery_logs/celery-worker-%n.log',
             '--pidfile=celery_logs/celery-worker-%n.pid'])
        os.system('pkill -f celery')
    except Exception:
        click.echo('Exception occurred. Run code locally')


@app.cli.command()
def restart_celery():
    """Kills then restarts the daemon process"""
    os.system('flask kill_celery')
    os.system('flask celery')


if __name__ == '__main__':
    app.secret_key = '\xd4S\x0e\x02w\x16\x86\xb1G\xdd\x7f\xc8%\xad\x8d\xc4\x86&\xce\xea:l5\xad'
    app.run(
        host=app.config.get("HOST", "localhost"),
        port=app.config.get("PORT", 8080),
        threaded=True
    )
