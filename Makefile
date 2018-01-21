# Flask Makefile
# Insert name of project into <PROJECT_NAME> in serve and db

venv:
	pip install virtualenv
	virtualenv venv
	source venv/bin/activate

install:
	echo "Installing packages from requirements.txt"
	venv/bin/pip install -r requirements.txt

serve:
	export FLASK_APP="run.py"; \
	flask run

migrate:
	export FLASK_APP="run.py"; \
	flask db migrate; \
	flask db upgrade

shell:
	export FLASK_APP="run.py"; \
	flask shell

# Azure deployment Makefile

create-azure-app:
	az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name cruzhacks2018 --runtime "python|3.4" --deployment-local-git

setup-git:
	git remote add azure https://aubhro20@cruzhacks2018.scm.azurewebsites.net/cruzhacks2018.git

deploy:
	git push azure master
