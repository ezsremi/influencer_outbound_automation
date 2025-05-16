import pandas as pd
import smtplib
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = ''  # Replace w/ email
EMAIL_PASSWORD = '' #Replace w/ app password









CPM_RATE = 10  # Set CPM rate in dollars
NAME = 'YOUR NAME HERE'
COMPANY = 'YOUR COMPANY HERE'
MAX_BUDGET = 3000

# Keyword-specific creator examples
CREATOR_REFERENCES = {
     "Valorant": [
        {"name": "Dittozkul", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Valorant Curios", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Doctor Freeze", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
    ],
    "Fortnite": [
        {"name": "Dittozkul", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Valorant Curios", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Doctor Freeze", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
    ],
    "Marvel Rivals": [
        {"name": "Dittozkul", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Valorant Curios", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Doctor Freeze", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
    ],
    "League of Legends": [
        {"name": "Dittozkul", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Valorant Curios", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Doctor Freeze", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
    ],
    "GTAV": [
        {"name": "Dittozkul", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Valorant Curios", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Doctor Freeze", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
    ],
    "Roblox": [
        {"name": "Dittozkul", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Valorant Curios", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
        {"name": "Doctor Freeze", "url": "https://www.youtube.com/ADD_YOUR_LINK_HERE"},
    ]
}

def generate_email(name, keyword, avg_views):
    creators = CREATOR_REFERENCES.get(keyword, [])
    if creators:
        creator_list = ", ".join(
            f'<a href="{creator["url"]}">{creator["name"]}</a>' for creator in creators
        )
    else:
        creator_list = "top creators in the space"

    estimated_earnings = min(MAX_BUDGET, round(CPM_RATE * avg_views / 1000))

    references_list = ["Valorant", "Marvel Rivals", "League of Legends", "Fortnite"]
    no_references_list = ["GTAV", "Roblox"]

    if keyword in references_list:
        # Default Template
        email_body = f"""
        <html>
          <body>
            <p>Hey {name},</p>

            <p>I'll keep this short - I'm {NAME} with <strong>{COMPANY}</strong>, a platform for "YOUR COMPANY MISSION". We've worked with creators in the <strong>{keyword}</strong> space like {creator_list}, and many more.</p>

            <p>Are you accepting video sponsorships right now? We're offering <strong>${CPM_RATE} CPM</strong> for a quick shoutout at the start of your next video – with your viewership, you could expect to make <strong>${estimated_earnings}</strong> from this partnership.</p>

            <p>If you're interested, want a different rate, or just curious, let me know and we can talk details.</p>

            <p>Look forward to hearing from you!<br>{NAME}</p>
          </body>
        </html>
        """

    elif keyword in no_references_list:
        # Special Template
        email_body = f"""
        <html>
          <body>
            <p>Hey {name},</p>

            <p>I'm {NAME} with <strong>{COMPANY}</strong> a trusted platform for "YOUR COMPANY MISSION" We've worked with creators in Valorant, Fortnite, Marvel Rivals, and more and are looking to expand to {keyword}. </p>

            <p>Are you accepting video sponsorships right now? We're looking to do 30-60 second integrated ads at the beginning of your next video, or a dedicated Youtube Short.</p>

            <p>If you're interested, could you let me know your standard rates for these engagements?</p>

            <p>Look forward to hearing from you!<br>{NAME}</p>
          </body>
        </html>
        """

    else:
        # Fallback Template
        email_body = f"""
        <html>
          <body>
            <p>Hey {name},</p>

            <p>I'm {NAME} from <strong>{COMPANY}</strong> – a platform for "YOUR COMPANY MISSION". We’re partnering with creators in games like <strong>{keyword}</strong> and would love to work with you.</p>

            <p>We’re offering <strong>${CPM_RATE} CPM</strong> for a sponsored video shoutout. With your average views, you’d be looking at around <strong>${estimated_earnings}</strong>.</p>

            <p>Let me know if you're open to it!</p>

            <p>Cheers,<br>{NAME}</p>
          </body>
        </html>
        """

    return email_body

def send_email(recipient, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"[Sent] Email sent to {recipient}")

            #random wait time to (attempt) to avoid spam flagging
            wait_time = random.randint(20, 80)
            print(f"Waiting {wait_time} seconds before sending the next email...")
            time.sleep(wait_time)
    except Exception as e:
        print(f"[Error] Failed to send email to {recipient}: {e}")

def main():
    df = pd.read_csv("influencers.csv")  # Adjust filename

    for _, row in df.iterrows():
        if pd.isna(row['email']):
            continue

        name = row['title']
        keyword = row['keyword']
        avg_views = float(row['avg_views'])
        email = row['email']

        subject = f"Can we sponsor your next {keyword} video?"
        body = generate_email(name, keyword, avg_views)

        send_email(email, subject, body)




if __name__ == "__main__":
    main()