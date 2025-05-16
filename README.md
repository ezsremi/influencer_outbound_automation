# influencer_outbound_automation
Used to automate cold outbound emailing for establishing contact with influencers.

**Problem:** Influencer funnel can be broken into three main stages: Outreach, Negotiation, and Delivery. This doc is focused on stage one. The Outreach process is a numbers game, especially when expanding to new games, and is currently a bottleneck and draws time away from skilled tasks in latter stages. The current process is:
slow & requires high manual labor on low skill, autonomize-able tasks not optimized for multiple people to work on outreach, leading to miscommunication

**Solution:** Leverage google APIs + freelancers (optional) for low-cost automation of stage 1, freeing up time for stage 2 + 3. 

**Ideal Workflow:**
![screenshot](Flowchart.jpg)

**⚙️Semi-Automated Workflow For Influencer Cold Outbound**
| Step | Tool | Manual or Automated? |
| ------------- | ------------- | ------------- |
| 1. Find influencers by content & stats | !(influencer_sourcing.py) | ✅ Automated |
| 2. Add data to central spreadsheet | CSV import. Need Google Sheets + Drive API access to automate (influencers.csv)
 | ✅ Semi-automated |
| 3. Get email for each influencer | (influencer_sourcing.py) | ✅ Automated |
| 1. Find influencers by content & stats | (influencer_sourcing.py) | ✅ Automated |
