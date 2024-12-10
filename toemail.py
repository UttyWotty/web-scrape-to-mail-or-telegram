import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to scrape the news
def scrape_news():
    url = "https://www.odatv.com/"   # change it weith a website you want to scrape
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find article headlines and links (assuming links are wrapped around the h2 tag or next to it)
    articles = []
    for item in soup.find_all('a', class_="swiper-pagination-bullet"):   # check the class name of the element you want to scrape
        headline = item.get('title')
        link = item.get('href')
        
        if headline and link:
            articles.append({'headline': headline, 'link': link})
           
    
    return articles[:5]  # Limiting to top 5 articles

# Testing the function
if __name__ == '__main__':
    articles = scrape_news()
    for article in articles:
        print(f"Headline: {article['headline']}\nLink: {article['link']}\n")

# Summarizing the content of each article
summarizer = pipeline('summarization', model='t5-small')

def summarize_article(article_link):
    response = requests.get(article_link)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extracting the article content
    paragraphs = soup.find_all('p')
    content = " ".join([paragraph.text for paragraph in paragraphs])

    # Debugging: Print the content to verify it's being extracted correctly
    print(f"Article content for {article_link}: {content[:500]}...")  # Print first 500 chars of content

    # Limit content to 1024 characters to avoid long input to the summarizer
    content = content[:1024]
    if not content:
        return 'Content unavailable'

    # Generate summary
    summary = summarizer(content, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# Sending email
def send_email(subject, body, recipient_email):
    sender_email = '****'  # Your email
    sender_password = '****'  # Your Gmail app password

    # Create message container (multipart)
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the body with MIMEText
    body_part = MIMEText(body, 'plain')  # 'plain' or 'html' if HTML body
    msg.attach(body_part)

    # Debugging: Print the email content before sending
    print("Email content being sent:")
    print(msg.as_string())

    try:
        # Send email via Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

# Main function to integrate all steps
def main():
    # Step 1: Scrape the news
    articles = scrape_news()

    # Step 2: Summarize each article
    summarize = []
    for article in articles:
        try:
            summary = summarize_article(article['link'])
            summarize.append(f"**{article['headline']}**\n{summary}\n")
            print(f"Article: {article['headline']} Summary: {summary}")  # Debugging each article
        except Exception as e:
            summarize.append(f"**{article['headline']}**\nSummary unavailable\n")
            print(f"Error summarizing article: {article['headline']} Error: {e}")  # Debugging errors

    # Step 3: Create the email body
    email_body = "\n".join(summarize)

    # Debugging: Check the email body before sending
    print(f"Email Body (before sending):\n{email_body}")  # Print to confirm it has content

    if not email_body.strip():
        email_body = "No articles available for today."

    # Step 4: Send email with the summaries
    send_email('Top 5 Articles from BBC News', email_body, '****@***.com')  # Recipient email

# Running the pipeline
if __name__ == '__main__':
    main()
