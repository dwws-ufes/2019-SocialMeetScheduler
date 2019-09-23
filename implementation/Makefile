depends: virtual_env
	. virtual_env/bin/activate; pip install -U -r requirements.frozen.txt

depends-latest: virtual_env
	. virtual_env/bin/activate; pip install -U -r requirements.txt

virtual_env:
	python3 -m virtualenv virtual_env
	make depends

removepycache:
	find webproj -name \*.pyc -delete
	find webproj -name __pycache__ -delete
	du -sh webproj

init: virtual_env
	. virtual_env/bin/activate; python manage.py migrate
	. virtual_env/bin/activate; python manage.py createcachetable
	- rm -rf static
	mkdir -p static
	. virtual_env/bin/activate; yes yes | python manage.py collectstatic

all: depends init virtual_env
	@echo ""
	@echo "Done"
	@echo ""

test: virtual_env
	-rm __init__.py
	. virtual_env/bin/activate; python manage.py test --noinput
	touch __init__.py

freeze:
	. virtual_env/bin/activate; python -m pip freeze > requirements.frozen.txt

fulldeploy: virtual_env
	-sudo rm -rf /var/www/meet/server_deploy_config
	-sudo rm -rf /var/www/meet/requirements.txt
	-sudo rm -rf /var/www/meet/requirements.frozen.txt
	-sudo rm -rf /var/www/meet/manage.py
	-sudo rm -rf /var/www/meet/Makefile
	-sudo rm -rf /var/www/meet/webproj
	-sudo rm -rf /var/www/meet/static
	-sudo mkdir -p /var/www/meet/static
	-sudo cp -rf ./server_deploy_config /var/www/meet/server_deploy_config
	-sudo cp -rf ./requirements.txt /var/www/meet/requirements.txt
	-sudo cp -rf ./requirements.frozen.txt /var/www/meet/requirements.frozen.txt
	-sudo cp -rf ./manage.py /var/www/meet/manage.py
	-sudo cp -rf ./Makefile /var/www/meet/Makefile
	-sudo cp -rf ./webproj /var/www/meet/webproj
	sudo make -C /var/www/meet depends
	sudo install ./server_deploy_config/meet-webapp.service /etc/systemd/system
	sudo install ./server_deploy_config/events-furmeet-app-http.conf /etc/nginx/sites-available
	-sudo mkdir -p /var/www/meet/media
	sudo systemctl daemon-reload
	sudo systemctl enable meet-webapp.service
	cd /var/www/meet; sudo chown http:http -R .
	sudo make -C /var/www/meet all
	sudo make -C /var/www/meet test
	sudo make -C /var/www/meet gzip_static_media
	cd /var/www/meet; sudo chown http:http -R .
	sudo systemctl restart meet-webapp.service
	sudo systemctl reload nginx.service

deploy: virtual_env
	-sudo rm -rf /var/www/meet/server_deploy_config
	-sudo rm -rf /var/www/meet/requirements.txt
	-sudo rm -rf /var/www/meet/requirements.frozen.txt
	-sudo rm -rf /var/www/meet/manage.py
	-sudo rm -rf /var/www/meet/Makefile
	-sudo rm -rf /var/www/meet/webproj
	-sudo rm -rf /var/www/meet/static
	-sudo mkdir -p /var/www/meet/static
	-sudo cp -rf ./server_deploy_config /var/www/meet/server_deploy_config
	-sudo cp -rf ./requirements.txt /var/www/meet/requirements.txt
	-sudo cp -rf ./requirements.frozen.txt /var/www/meet/requirements.frozen.txt
	-sudo cp -rf ./manage.py /var/www/meet/manage.py
	-sudo cp -rf ./Makefile /var/www/meet/Makefile
	-sudo cp -rf ./webproj /var/www/meet/webproj
	sudo make -C /var/www/meet depends
	sudo install ./server_deploy_config/meet-webapp.service /etc/systemd/system
	-sudo mkdir -p /var/www/meet/media
	sudo systemctl daemon-reload
	sudo systemctl enable meet-webapp.service
	cd /var/www/meet; sudo chown http:http -R .
	sudo make -C /var/www/meet all
	sudo make -C /var/www/meet test
	sudo make -C /var/www/meet gzip_static_media
	cd /var/www/meet; sudo chown http:http -R .
	sudo systemctl restart meet-webapp.service

gzip_static_media:
	-find ./static -name "*.gz" | xargs rm
	-find ./media -name "*.gz" | xargs rm
	-gzip -frk9 ./static
	-gzip -frk9 ./media

serve: virtual_env
	. virtual_env/bin/activate; (\
		virtual_env/bin/uwsgi \
			--http :19843 \
			--virtualenv virtual_env \
			--module webproj.wsgi \
			--master --enable-threads \
			--threads 3 \
			--workers 8 \
	)

addlang:
	. virtual_env/bin/activate; cd webproj; python ../manage.py makemessages -l $(LANG)

new-superuser:
	. virtual_env/bin/activate; python manage.py createsuperuser

devserver: virtual_env
	-@mkdir -p static
	. virtual_env/bin/activate; python manage.py makemigrations
	. virtual_env/bin/activate; python manage.py migrate
	. virtual_env/bin/activate; python manage.py createcachetable
	. virtual_env/bin/activate; yes yes | python manage.py collectstatic
	. virtual_env/bin/activate; python manage.py runserver 0.0.0.0:8000

devserverprod: virtual_env
	. virtual_env/bin/activate; python manage.py runserver 0.0.0.0:19843
