FROM archlinux

MAINTAINER Adler Neves "adlerosn@gmail.com"

ENV PYTHONUNBUFFERED=1
ENV LANG=en_US.UTF-8

RUN mkdir -p /var/www/meet
RUN pacman -Suy python gdal python-virtualenv base-devel automake --noconfirm --needed

CMD /usr/sbin/make all serve -C /var/www/meet

EXPOSE 19843