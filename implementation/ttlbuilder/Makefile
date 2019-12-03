tdb: tmp.ttl
	tdbloader2 --loc tdb tmp.ttl
	rm tmp.ttl

tmp.ttl: download
	rm -f tmp.ttl
	touch tmp.ttl
	for i in $$(cat ttls.txt | rev | cut -d'/' -f1 | rev); do bzip2 -kdc $$i >> tmp.ttl; done

download:
	for i in $$(cat ttls.txt); do wget -c $$i; done
	touch download

