# poc_monitor
A short scraper looking for a POC of CVE-2024-49112

Setting a cron job to run the script every 4 hours will keep the updates in place. The alerting can be customized but used Discord webhook to alert a Discord channel. 

`0 */4 * * * cd /root/monitor_script && /usr/bin/python3 poc_monitor.py >> /var/log/poc_monitor/poc_monitor.log 2>&1`

with a debug set:

`cd /root/monitor_script && /usr/bin/python3 poc_monitor.py >> /var/log/poc_monitor/poc_monitor.log 2>&1 || echo "Cron job failed at $(date)" >> /var/log/poc_monitor/poc_monitor.log`

Set your .env file like so:
```
GOOGLE_API_KEY=your_google_api_key
SEARCH_ENGINE_ID=your_search_engine_id
DISCORD_WEBHOOK_URL=your_discord_webhook_url
SEARCH_TERM=POC CVE-2024-XXXX
CHECK_INTERVAL=14400  # in seconds (4 hours)
```
Obviously you can set the search term to whatever you want, just be careful about timing since the Google search API isn't free above 100 queries a day.
