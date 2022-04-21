#!/bin/bash
set -e

eval $(ssh-agent -s)

cd /home/pi/scripts/block.txt

cat ~/scripts/block.txt/gaminglaptop.txt  | grep 0\.0\.0\.0\ .*[a-z] | awk '{print $2}' | sort | uniq > /tmp/gaminglaptop.tmp

sqlite3 /etc/pihole/pihole-FTL.db 'select domain, COUNT (*) from queries where status in (1,4,5,6,7,8,9,10,11) AND client == "10.0.0.15" GROUP BY domain HAVING COUNT(*) > 6 ORDER BY COUNT(*) DESC' | \
	sed -e 's/|.*//g' | grep -v -E 'redditmedia|lastpass|www.google.com' >> /tmp/gaminglaptop.tmp

sort /tmp/gaminglaptop.tmp | uniq > /tmp/gaminglaptop.txt
echo "# Generated on" $(date) "with" $(wc -l /tmp/gaminglaptop.txt | awk '{print $1}') "records" > ./gaminglaptop.txt
cat /tmp/gaminglaptop.txt | awk '{print "0.0.0.0 " $1}' >> ./gaminglaptop.txt
rm /tmp/gaminglaptop.tmp
git diff
sleep 10
git add ./gaminglaptop.txt
git commit -m "Generated $(date)"
git push
