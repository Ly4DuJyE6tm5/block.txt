#!/bin/bash

cd /home/pi/scripts/block.txt

cat ~/scripts/block.txt/blokada.txt  | grep 0\.0\.0\.0\ .*[a-z] | awk '{print $2}' | sort | uniq > /tmp/blokada.tmp

sqlite3 /etc/pihole/pihole-FTL.db 'select domain, COUNT (*) from queries where status in (1,4,5,6,7,8,9,10,11) AND client == "10.0.0.23" GROUP BY domain HAVING COUNT(*) > 9 ORDER BY COUNT(*) DESC' | \
	sed -e 's/|.*//g' >> /tmp/blokada.tmp

sort /tmp/blokada.tmp | uniq > /tmp/blokada.txt
echo "# Generated on" $(date) "with" $(wc -l /tmp/blokada.txt | awk '{print $1}') "records" > ./blokada.txt
cat /tmp/blokada.txt | awk '{print "0.0.0.0 " $1}' >> ./blokada.txt
rm /tmp/blokada.tmp
git add ./blokada.txt
git commit -m "Generated $(date)"
git push
