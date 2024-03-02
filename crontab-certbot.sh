cd /src/digital-clinical-safety-platform
/usr/bin/docker compose -f docker-compose-prod.yml run --rm certbot-prod certonly --webroot --webroot-path /var/www/certbot/ --noninteractive --agree-tos --expand --email mark.allan.bailey@gmail.com -d dcsalliance.org -d www.dcsalliance.org >> /src/digital-clinical-safety-platform/logs/certbot/cerbot.log 2>&1