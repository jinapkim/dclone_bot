# DClone Discord Bot for Diablo II:Resurrected
-----
This is a Discord bot that uses the Diablo Clone Tracker API from diablo2.io to track and report progress of Diablo Clones across all regions and game 
modes in Diablo 2. It automatically reports changes in progress at or above level 3 (out of 6). Users can use the command /dclone [region] [ladder] [hc] 
to get a most recent progress update and filter the results. 

-----
How to Install and Run the Bot
1. Log onto the Discord website
2. Create a New Application
3. Invite the bot to your server
4. Download the bot and set API_TOKEN to the token from your application's page on the Discord website. Set CHANNEL_ID to the ID of the
   channel where you want automatic updates to be sent.
5. Start the bot using:
     python dclone.py

* Data courtesy of  diablo2.io (https://diablo2.io/dclonetracker.php)
