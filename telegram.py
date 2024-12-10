import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# Telegram bot details
BOT_TOKEN = '****'  # Replace with your bot's API token , check https://core.telegram.org/bots#6-botfather
CHAT_ID = '****'          # Replace with your chat ID , check https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id

# Function to send a message via Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,   
        'text': message,
        'parse_mode': 'Markdown'  # Optional: Use Markdown for formatting
    }
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Error: {response.text}")

# Function to scrape the news   
def scrape_news():
    url = "https://www.odatv.com/"   # change it to the website you want to scrape
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find article headlines and links
    articles = []
    for item in soup.find_all('a', class_="swiper-pagination-bullet"):   # if you are using a different website, you may need to change the class name
        headline = item.get('title')   # inspect the website to find the correct tag and class name
        link = item.get('href')
        
        if headline and link:
            articles.append({'headline': headline, 'link': link})
    
    return articles[:5]  # Limiting to top 5 articles

# Summarizing the content of each article
summarizer = pipeline('summarization', model='t5-small')

def summarize_article(article_link):
    response = requests.get(article_link)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extracting the article content
    paragraphs = soup.find_all('p')
    content = " ".join([paragraph.text for paragraph in paragraphs])

    # Limit content to 1024 characters to avoid long input to the summarizer
    content = content[:1024]
    if not content.strip():
        return 'Content unavailable'

    # Generate summary
    summary = summarizer(content, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# Main function to integrate all steps
def main():
    # Step 1: Scrape the news
    articles = scrape_news()

    # Step 2: Summarize each article
    summaries = []
    for article in articles:
        try:
            summary = summarize_article(article['link'])
            summaries.append(f"**{article['headline']}**\n{summary}\n[Read more]({article['link']})\n")
            print(f"Article: {article['headline']} Summary: {summary}")  # Debugging each article
        except Exception as e:
            summaries.append(f"**{article['headline']}**\nSummary unavailable\n[Read more]({article['link']})\n")
            print(f"Error summarizing article: {article['headline']} Error: {e}")  # Debugging errors

    # Step 3: Create the Telegram message
    telegram_message = "\n\n".join(summaries)

    # Debugging: Check the Telegram message content
    print(f"Telegram Message (before sending):\n{telegram_message}")  # Print to confirm it has content

    if not telegram_message.strip():
        telegram_message = "No articles available for today."

    # Step 4: Send the summaries to Telegram
    send_telegram_message(telegram_message)

# Running the pipeline
if __name__ == '__main__':
    main()
