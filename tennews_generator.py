# TENNEWS DAILY DIGEST - GITHUB VERSION
# Automated news selection and generation for Next.js website

import requests
import json
from datetime import datetime, timedelta, timezone
import time
import os
from bs4 import BeautifulSoup
import re
import pytz
import pandas as pd

# ==================== API KEY CONFIGURATION ====================
# Get API key from GitHub secrets (for automation) or environment variable
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', 'your-api-key-here-for-testing')

# Claude Models
CLAUDE_MODEL = "claude-opus-4-1-20250805"
CLAUDE_SONNET_MODEL = "claude-3-5-sonnet-20241022"

# Files for storage
EXCEL_FILE = 'news_archive.xlsx'
OUTPUT_JSON = 'public/news_data.json'

# ==================== APPROVED NEWS SOURCES ====================
ALLOWED_DOMAINS = [
    "reuters.com", "apnews.com", "afp.com", "nytimes.com", "washingtonpost.com",
    "wsj.com", "usatoday.com", "cnn.com", "nbcnews.com", "abcnews.go.com",
    "cbsnews.com", "npr.org", "foxnews.com", "foxbusiness.com", "msnbc.com",
    "cnbc.com", "bloomberg.com", "marketwatch.com", "ft.com", "barrons.com",
    "fool.com", "seekingalpha.com", "bbc.com", "theguardian.com", "telegraph.co.uk",
    "thetimes.co.uk", "independent.co.uk", "euronews.com", "politico.eu", "politico.com",
    "lemonde.fr", "france24.com", "lefigaro.fr", "spiegel.de", "zeit.de",
    "welt.de", "elpais.com", "corriere.it", "japantimes.co.jp", "scmp.com",
    "straitstimes.com", "timesofindia.com", "thehindu.com", "koreaherald.com", "koreatimes.co.kr",
    "channelnewsasia.com", "asia.nikkei.com", "asiatimes.com", "thediplomat.com", "nzherald.co.nz",
    "abc.net.au", "smh.com.au", "theaustralian.com.au", "inquirer.net", "bangkokpost.com",
    "aljazeera.com", "haaretz.com", "jpost.com", "arabnews.com", "timesofisrael.com",
    "al-monitor.com", "i24news.tv", "africanews.com", "allafrica.com", "cnbcafrica.com",
    "theafricareport.com", "businessday.co.za", "african.business", "batimes.com.ar", "riotimesonline.com",
    "forbes.com", "fortune.com", "businessinsider.com", "fastcompany.com", "inc.com",
    "entrepreneur.com", "hbr.org", "techcrunch.com", "venturebeat.com", "wired.com",
    "arstechnica.com", "theverge.com", "theinformation.com", "mashable.com", "engadget.com",
    "thenextweb.com", "geekwire.com", "axios.com", "vox.com", "theintercept.com",
    "qz.com", "morningbrew.com", "finance.yahoo.com", "investing.com", "thestreet.com",
    "investors.com", "kiplinger.com", "news.crunchbase.com", "cbinsights.com", "pitchbook.com",
    "sifted.eu", "eu-startups.com", "tech.eu", "alleywatch.com", "builtin.com",
    "yourstory.com", "e27.co", "mckinsey.com", "bcg.com", "bain.com",
    "deloitte.com", "pwc.com", "sloanreview.mit.edu", "gsb.stanford.edu", "prnewswire.com",
    "businesswire.com", "industrydive.com", "nature.com", "science.org", "scientificamerican.com",
    "newscientist.com", "phys.org", "sciencedaily.com", "eurekalert.org", "livescience.com",
    "space.com", "nasa.gov", "esa.int", "arxiv.org", "plos.org",
    "cell.com", "thelancet.com", "nejm.org", "jama.jamanetwork.com", "bmj.com",
    "ieee.org", "acm.org", "kaggle.com", "datasciencecentral.com", "kdnuggets.com",
    "towardsdatascience.com", "fivethirtyeight.com", "ourworldindata.org", "statista.com", "pewresearch.org"
]

ALLOWED_DOMAINS_SET = set(ALLOWED_DOMAINS)

# ==================== EXCEL STORAGE FUNCTIONS ====================
def initialize_excel_file():
    """Create Excel file if it doesn't exist"""
    if not os.path.exists(EXCEL_FILE):
        print("📊 Creating new Excel archive file...")
        df = pd.DataFrame(columns=[
            'Date', 'Rank', 'Title', 'Summary', 'Source', 'URL', 
            'Category', 'Importance', 'DailyGreeting', 'ReadingTime',
            'FormattedDate', 'Emoji'
        ])
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        print("✅ Excel archive created!")

def fetch_previous_articles_from_excel():
    """Fetch the last 2 weeks of articles from Excel file"""
    try:
        if not os.path.exists(EXCEL_FILE):
            print("📊 No previous articles found (new archive)")
            return []
        
        print("\n📚 Reading previous articles from Excel...")
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        
        if df.empty:
            print("📊 Excel file is empty (no previous articles)")
            return []
        
        # Filter last 14 days
        df['Date'] = pd.to_datetime(df['Date'])
        cutoff_date = datetime.now() - timedelta(days=14)
        recent_df = df[df['Date'] >= cutoff_date]
        
        previous_articles = []
        for _, row in recent_df.iterrows():
            previous_articles.append({
                'title': row['Title'],
                'summary': row['Summary'],
                'source': row['Source'],
                'sourceUrl': row['URL']
            })
        
        print(f"✅ Retrieved {len(previous_articles)} articles from last 2 weeks")
        return previous_articles
        
    except Exception as e:
        print(f"⚠️ Error reading Excel: {str(e)[:100]}")
        return []

def save_articles_to_excel(articles_data, daily_greeting, reading_time, formatted_date):
    """Save today's articles to Excel file"""
    try:
        print("\n💾 Saving articles to Excel archive...")
        
        # Read existing data or create new DataFrame
        if os.path.exists(EXCEL_FILE):
            df_existing = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        else:
            df_existing = pd.DataFrame()
        
        # Prepare new data
        new_rows = []
        for article in articles_data['articles']:
            new_rows.append({
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Rank': article['rank'],
                'Title': article['title'],
                'Summary': article['summary'],
                'Source': article['source'],
                'URL': article['url'],
                'Category': article['category'],
                'Importance': article.get('importance', 'High'),
                'DailyGreeting': daily_greeting,
                'ReadingTime': reading_time,
                'FormattedDate': formatted_date,
                'Emoji': article['emoji']
            })
        
        df_new = pd.DataFrame(new_rows)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # Save to Excel
        df_combined.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        print(f"✅ Saved {len(new_rows)} articles to Excel archive")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving to Excel: {str(e)[:100]}")
        return False

# ==================== UTILITY FUNCTIONS ====================
def clean_text_for_json(text):
    """Clean text to be JSON-safe"""
    if not text:
        return ""
    
    text = str(text)
    text = text.replace('"', "'")
    text = text.replace('\\', '\\\\')
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')
    
    text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    
    text = text.strip()
    if len(text) > 500:
        text = text[:497] + "..."
    
    return text

def clean_json_response(content):
    """Clean and fix common JSON issues in GDELT responses"""
    if content.startswith('\ufeff'):
        content = content[1:]
    
    content = content.replace('\\\\', '\\')
    
    first_brace = content.find('{')
    last_brace = content.rfind('}')
    
    if first_brace >= 0 and last_brace > first_brace:
        content = content[first_brace:last_brace + 1]
    
    return content

def get_formatted_date():
    """Get formatted date in UK timezone - all capitals"""
    uk_tz = pytz.timezone('Europe/London')
    uk_time = datetime.now(uk_tz)
    return uk_time.strftime("%A, %B %-d, %Y").upper()

def generate_daily_greeting_and_reading_time(top_articles):
    """Generate AI-powered greeting based on today's news or special occasions"""
    uk_tz = pytz.timezone('Europe/London')
    uk_time = datetime.now(uk_tz)
    
    total_words = sum(len(article.get('summary', '').split()) for article in top_articles)
    titles = [article.get('title', '') for article in top_articles]
    
    prompt = f"""Today is {uk_time.strftime('%B %d, %Y')} ({uk_time.strftime('%A')}).

TASK: Create a daily greeting for news readers. The AI should decide whether to use "Good morning" or mention a special day if it's a famous holiday or important date.

REQUIREMENTS:
1. Start with either "Good morning," OR a special day greeting if today is special (e.g., "Happy New Year," "Merry Christmas," etc.)
2. Add a comma, then in MAXIMUM 10 words total (including the greeting), write something important or interesting about today
3. Use B2 level English (intermediate - clear but not complex)
4. Make it engaging and NOT boring
5. It can be about the news OR about what makes today special
6. Keep the ENTIRE greeting under 10 words total

GOOD EXAMPLES:
- "Good morning, democracy wins as dictator falls unexpectedly"
- "Happy Valentine's Day, love conquers global market chaos"
- "Good morning, world celebrates breakthrough cancer treatment discovery"
- "Merry Christmas, peace talks bring hope worldwide"
- "Good morning, climate victory as emissions drop dramatically"
- "Happy New Year, fresh start with global cooperation"

BAD EXAMPLES (too generic/boring):
- "Good morning, lots of news today"
- "Good morning, interesting things are happening"
- "Good morning, busy day ahead"

Today's top headlines for context:
{json.dumps(titles[:5], indent=2)}

ALSO calculate the reading time for a digest with {total_words} words total:
- Use 200-250 words per minute average reading speed
- Round to the nearest minute
- If less than 1 minute, say "1 minute read"

Return in this EXACT format:
{{
  "greeting": "your complete greeting under 10 words",
  "reading_time": "X minute read"
}}

Return ONLY the JSON, nothing else."""
    
    response = call_claude_api_with_model(prompt, "Generating daily greeting and reading time", CLAUDE_SONNET_MODEL)
    
    if response:
        try:
            parsed = parse_json_with_fallback(response)
            if parsed:
                daily_greeting = parsed.get('greeting', 'Good morning, today brings important global updates')
                reading_time = parsed.get('reading_time', '5 minute read')
                return daily_greeting, reading_time
        except Exception as e:
            print(f"⚠️ Error parsing greeting response: {str(e)[:100]}")
    
    estimated_minutes = max(1, round(total_words / 225))
    return "Good morning, today brings important global updates", f"{estimated_minutes} minute read"

def generate_historical_events():
    """Generate historical events that occurred on today's date"""
    uk_tz = pytz.timezone('Europe/London')
    uk_time = datetime.now(uk_tz)
    current_month = uk_time.strftime('%B')
    current_day = uk_time.day
    
    print(f"\n📚 Generating historical events for {current_month} {current_day}...")
    
    prompt = f"""Research and find 4 historical events that occurred on {current_month} {current_day} throughout history. Please follow these specific requirements:

Research Requirements:
- Use web search to find reliable historical sources about events that happened on {current_month} {current_day}
- Look for events from different time periods (spread across centuries)
- Focus on events from diverse categories - don't repeat similar topics (for example, avoid having two events about the same person, country, or topic type)
- Verify dates carefully to ensure they actually occurred on {current_month} {current_day}

Selection Criteria:
- Choose events that are globally significant and would be recognized by many people worldwide
- Select events that had major historical impact or cultural significance
- Include a mix of different types of events (could include: major battles, scientific discoveries, cultural milestones, political revolutions, sports achievements, artistic/cultural events, etc.)
- Prioritize events that are interesting and memorable rather than obscure facts

Format Requirements:
- Present exactly 4 events as bullet points
- Start each bullet with the year the event occurred
- Keep each description to a maximum of 10 words
- Use clear, simple language that anyone could understand
- Write in this format: "• [YEAR]: [Event description in 10 words or less]"

Examples of good format:
• 1485: King Richard III defeated at Battle of Bosworth Field
• 1969: Neil Armstrong walks on the moon for first time

What to avoid:
- Don't include two events about the same topic (like two Beatles events)
- Don't use complex or technical language
- Don't exceed the 10-word limit per event
- Don't include minor or locally-specific events that most people wouldn't know

Please search thoroughly and select the most significant and interesting events that meet all these criteria.

Return ONLY a JSON object in this format:
{{
  "events": [
    {{
      "year": "1485",
      "description": "King Richard III defeated at Battle of Bosworth Field"
    }},
    {{
      "year": "1969",
      "description": "Neil Armstrong walks on the moon for first time"
    }},
    {{
      "year": "YEAR3",
      "description": "Event 3 description"
    }},
    {{
      "year": "YEAR4",
      "description": "Event 4 description"
    }}
  ]
}}

Return ONLY the JSON, nothing else."""
    
    response = call_claude_api_with_model(prompt, "Generating historical events", CLAUDE_SONNET_MODEL)
    
    if response:
        try:
            parsed = parse_json_with_fallback(response)
            if parsed and 'events' in parsed:
                events = parsed['events']
                print(f"✅ Generated {len(events)} historical events")
                
                print("\n📅 Historical Events for Today:")
                for event in events:
                    print(f"   • {event['year']}: {event['description']}")
                
                return events
        except Exception as e:
            print(f"⚠️ Error parsing historical events response: {str(e)[:100]}")
    
    print("⚠️ Using fallback historical events")
    return [
        {"year": "1485", "description": "Battle of Bosworth Field ends War of Roses"},
        {"year": "1864", "description": "Geneva Convention for wounded soldiers first signed"},
        {"year": "1911", "description": "Mona Lisa stolen from the Louvre Museum"},
        {"year": "1968", "description": "Pope Paul VI arrives in Colombia, first papal visit"}
    ]

def parse_gdelt_date(date_string):
    """Parse GDELT date format: 20250716T120000Z"""
    if not date_string or len(date_string) < 15:
        return None
    
    try:
        year = int(date_string[0:4])
        month = int(date_string[4:6])
        day = int(date_string[6:8])
        hour = int(date_string[9:11])
        minute = int(date_string[11:13])
        second = int(date_string[13:15])
        
        return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    except Exception as e:
        print(f"⚠️ Error parsing date {date_string}: {str(e)[:50]}")
        return None

def fetch_gdelt_news_last_24_hours():
    """Fetch important news from GDELT sorted by relevance"""
    print(f"🌍 Fetching global news from GDELT (approved sources only)...")
    print(f"🔥 Using hybrid relevance sorting for importance-based ranking")
    print(f"📰 Fetching up to 250 articles per query")
    print(f"Time period: Last 24 hours")
    print("=" * 70)
    
    all_articles = []
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    search_queries = [
        "(breaking OR urgent OR crisis OR emergency OR unprecedented OR historic OR exclusive OR BREAKING OR URGENT)",
        "(killed OR died OR death OR casualties OR victims OR injured OR wounded OR fatalities OR toll)",
        "(billion OR trillion OR million OR record OR highest OR lowest OR surge OR plunge OR soar OR crash)",
        "(market OR stocks OR earnings OR IPO OR merger OR acquisition OR bankrupt OR revenue OR profit OR loss)",
        "(Fed OR inflation OR recession OR GDP OR unemployment OR economy OR rates OR dollar OR euro OR yuan)",
        "(AI OR artificial intelligence OR robot OR quantum OR breakthrough OR discovery OR innovation OR research OR study)",
        "(SpaceX OR NASA OR vaccine OR cure OR climate OR cancer OR treatment OR therapy OR disease OR pandemic)",
        "(index OR ranking OR study OR survey OR report OR statistics OR poll OR data OR analysis OR forecast)",
        "(attack OR explosion OR collapse OR disaster OR conflict OR war OR battle OR strike OR protest OR riot)",
        "(announced OR launched OR revealed OR unveiled OR discovered OR confirmed OR admitted OR denied)",
        "(CEO OR executive OR resign OR appointed OR fired OR promoted OR stepped down OR retirement OR succession)",
        "(merger OR acquisition OR buyout OR takeover OR deal OR purchase OR bid OR offer OR valuation)",
        "(ChatGPT OR GPT OR LLM OR neural network OR machine learning OR deep learning OR AGI OR OpenAI OR Anthropic)",
        "(bitcoin OR cryptocurrency OR blockchain OR ethereum OR crypto OR NFT OR DeFi OR mining OR wallet)",
        "(climate change OR global warming OR carbon OR emissions OR renewable energy OR solar OR wind OR net zero)",
        "(FDA approval OR medical breakthrough OR clinical trial OR drug OR medicine OR treatment OR cure OR therapy)",
        "(startup OR funding OR venture capital OR unicorn OR Series A OR Series B OR IPO OR valuation OR investment)",
        "(sanctions OR tensions OR diplomatic OR embassy OR relations OR summit OR treaty OR agreement OR talks)",
        "(oil OR gas OR OPEC OR energy OR pipeline OR renewable OR nuclear OR coal OR electricity OR power)",
        "(central bank OR interest rate OR monetary policy OR Federal Reserve OR ECB OR BOE OR BOJ OR stimulus)",
        "(supply chain OR shipping OR logistics OR shortage OR disruption OR container OR port OR delivery)",
        "(cyber attack OR hack OR data breach OR ransomware OR security OR vulnerability OR password OR encryption)",
        "(space station OR satellite OR Mars OR moon OR astronaut OR rocket OR launch OR orbit OR mission)",
        "(university OR education OR scholarship OR research grant OR Nobel OR academic OR school OR student)",
        "(Olympics OR World Cup OR championship OR transfer OR contract OR stadium OR league OR tournament)",
        "(Amazon OR retail OR e-commerce OR sales OR shopping OR consumer OR store OR online OR delivery)",
        "(Tesla OR electric vehicle OR autonomous OR car OR automotive OR EV OR battery OR charging OR factory)",
        "(real estate OR housing OR mortgage OR property OR construction OR rent OR prices OR development)",
        "(regulation OR compliance OR fine OR lawsuit OR antitrust OR investigation OR probe OR penalty OR ruling)",
        "(population OR demographic OR migration OR census OR aging OR birth rate OR immigration OR refugee)",
        "(Apple OR Google OR Microsoft OR Meta OR Facebook OR Twitter OR X OR TikTok OR Instagram)",
        "(Biden OR Putin OR Xi Jinping OR Trump OR Zelensky OR Modi OR Macron OR Netanyahu)",
        "(JPMorgan OR Bank of America OR Wells Fargo OR Citigroup OR Goldman Sachs OR Morgan Stanley)",
        "(Boeing OR Airbus OR airline OR flight OR aviation OR crash OR safety OR pilot)",
        "(Netflix OR Disney OR Hollywood OR movie OR film OR streaming OR box office OR Oscar)",
        "(food OR agriculture OR farming OR crop OR harvest OR famine OR hunger OR prices)",
        "(insurance OR hurricane OR earthquake OR flood OR wildfire OR tornado OR damage OR claims)",
        "(Pfizer OR Moderna OR Johnson OR vaccine OR drug OR pharmaceutical OR FDA OR clinical)",
        "(viral OR trending OR social media OR influencer OR platform OR content OR creator)",
        "(election OR vote OR poll OR campaign OR candidate OR primary OR ballot OR democracy)"
    ]
    
    query_labels = {
        1: "General Breaking News",
        2: "Human Impact/Casualties",
        3: "Major Scale Stories",
        4: "Business/Finance News",
        5: "Economic Indicators",
        6: "Science/Technology",
        7: "Space/Medical/Climate",
        8: "Data Rankings/Studies",
        9: "Conflicts/Disasters",
        10: "Major Announcements",
        11: "Corporate Leadership",
        12: "Mergers & Acquisitions",
        13: "AI & Machine Learning",
        14: "Cryptocurrency/Blockchain",
        15: "Climate Change/Environment",
        16: "Medical Breakthroughs",
        17: "Startup/Venture Capital",
        18: "Geopolitical Tensions",
        19: "Energy/Oil Markets",
        20: "Central Bank Policy",
        21: "Supply Chain/Logistics",
        22: "Cybersecurity/Breaches",
        23: "Space Exploration",
        24: "Education/Rankings",
        25: "Sports Business",
        26: "Retail/E-commerce",
        27: "Automotive/EVs",
        28: "Real Estate/Housing",
        29: "Regulatory/Compliance",
        30: "Demographics/Population",
        31: "Major Tech Companies",
        32: "World Leaders",
        33: "Major Banks",
        34: "Aviation",
        35: "Entertainment",
        36: "Food & Agriculture",
        37: "Insurance & Disaster",
        38: "Pharma",
        39: "Social Media",
        40: "Elections"
    }
    
    print("\n🔍 Searching for important news across categories...")
    
    for idx, query in enumerate(search_queries, 1):
        label = query_labels.get(idx, f"Search {idx}")
        print(f"\n📋 {label}: {query[:40]}...")
        
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": "250",
            "timespan": "1d",
            "sort": "hybridrel"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                if content.startswith('<!DOCTYPE') or content.startswith('<html'):
                    print(f"   ❌ Got HTML response, skipping...")
                    continue
                
                try:
                    cleaned_content = clean_json_response(content)
                    data = json.loads(cleaned_content)
                    articles = data.get('articles', [])
                    
                    valid_articles = 0
                    for article in articles:
                        if article.get('title') and article.get('url'):
                            article['title'] = clean_text_for_json(article.get('title', ''))
                            all_articles.append(article)
                            valid_articles += 1
                    
                    print(f"   ✓ Found {valid_articles} articles")
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ Failed to parse JSON response: {str(e)[:100]}")
                    try:
                        import re
                        url_pattern = r'"url"\s*:\s*"([^"]+)"'
                        title_pattern = r'"title"\s*:\s*"([^"]+)"'
                        
                        urls = re.findall(url_pattern, content)
                        titles = re.findall(title_pattern, content)
                        
                        if urls and titles:
                            valid_articles = 0
                            for url, title in zip(urls[:250], titles[:250]):
                                if url and title:
                                    all_articles.append({
                                        'url': url,
                                        'title': clean_text_for_json(title)
                                    })
                                    valid_articles += 1
                            print(f"   ✓ Recovered {valid_articles} articles using fallback parsing")
                        else:
                            print(f"   ❌ Could not recover articles from response")
                    except Exception as e2:
                        print(f"   ❌ Fallback parsing also failed: {str(e2)[:50]}")
                    
            elif response.status_code == 429:
                print(f"   ⚠️ Rate limited, waiting 2 seconds...")
                time.sleep(2)
            else:
                print(f"   ❌ Error {response.status_code}")
                
            time.sleep(2)
            
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timed out")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {str(e)[:100]}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)[:100]}")
    
    return all_articles

def extract_base_domain(url):
    """Extract base domain from URL, handling subdomains properly"""
    try:
        if url.startswith('http://'):
            domain = url[7:].split('/')[0]
        elif url.startswith('https://'):
            domain = url[8:].split('/')[0]
        else:
            domain = url.split('/')[0]
        
        domain = domain.replace('www.', '')
        
        parts = domain.split('.')
        if len(parts) > 2:
            if parts[-2] in ['co', 'com', 'net', 'org', 'gov', 'edu', 'ac']:
                base_domain = '.'.join(parts[-3:])
            else:
                base_domain = '.'.join(parts[-2:])
        else:
            base_domain = domain
            
        return base_domain
    except Exception as e:
        print(f"   ⚠️ Error extracting domain from {url[:50]}...: {str(e)[:50]}")
        return None

def deduplicate_articles(articles):
    """Remove duplicate articles based on URL and filter by approved domains"""
    print(f"\n🔄 Processing and filtering articles...")
    unique_articles = []
    seen_urls = set()
    approved_count = 0
    rejected_count = 0
    rejected_domains = set()
    subdomain_matches = 0
    
    for article in articles:
        url = article.get('url', '').lower()
        if url and url not in seen_urls:
            base_domain = extract_base_domain(url)
            
            if base_domain:
                if base_domain in ALLOWED_DOMAINS_SET:
                    seen_urls.add(url)
                    article['domain'] = base_domain
                    unique_articles.append(article)
                    approved_count += 1
                    
                    if '.' in url.split('/')[2].replace('www.', '').replace(base_domain, ''):
                        subdomain_matches += 1
                else:
                    rejected_count += 1
                    rejected_domains.add(base_domain)
            else:
                rejected_count += 1
    
    print(f"- Total articles fetched: {len(articles):,}")
    print(f"- Articles from approved sources: {approved_count:,}")
    print(f"  (Including {subdomain_matches} subdomain matches)")
    print(f"- Articles rejected (not from approved sources): {rejected_count:,}")
    
    if rejected_domains and len(rejected_domains) <= 10:
        print(f"- Sample rejected domains: {', '.join(list(rejected_domains)[:10])}")
    
    print(f"- Unique articles from approved sources: {len(unique_articles):,}")
    
    return unique_articles

def detect_article_category(article):
    """Simple category detection based on URL and domain"""
    url = article.get('url', '').lower()
    domain = article.get('domain', '').lower()
    
    business_domains = ['bloomberg.com', 'marketwatch.com', 'cnbc.com', 'forbes.com', 
                       'fortune.com', 'wsj.com', 'ft.com', 'businessinsider.com',
                       'fool.com', 'seekingalpha.com', 'barrons.com', 'investing.com']
    
    tech_domains = ['techcrunch.com', 'wired.com', 'theverge.com', 'arstechnica.com',
                   'venturebeat.com', 'engadget.com', 'mashable.com', 'theinformation.com']
    
    science_domains = ['nature.com', 'science.org', 'scientificamerican.com', 'newscientist.com',
                      'phys.org', 'sciencedaily.com', 'eurekalert.org', 'livescience.com']
    
    if any(pattern in url for pattern in ['/business/', '/finance/', '/markets/', 
                                         '/economy/', '/money/', '/stocks/']):
        return 'Business News'
    
    if any(pattern in url for pattern in ['/technology/', '/tech/', '/science/', 
                                         '/innovation/', '/computing/', '/ai/']):
        return 'Science and Technology News'
    
    if any(pattern in url for pattern in ['/ranking/', '/index/', '/statistics/', 
                                         '/data/', '/survey/', '/study/', '/report/']):
        return 'Data & Analytics News'
    
    if domain in business_domains:
        return 'Business News'
    
    if domain in tech_domains:
        return 'Science and Technology News'
    
    if domain in science_domains:
        return 'Science and Technology News'
    
    return 'General News'

def create_selection_prompt(articles, previous_articles=None):
    """Create prompt for Claude to select top 10 most important news stories"""
    
    formatted_articles = []
    for i, article in enumerate(articles):
        formatted_articles.append({
            "id": i,
            "title": clean_text_for_json(article.get('title', '')),
            "url": article.get('url', ''),
            "domain": article.get('domain', '')
        })
    
    previous_context = ""
    if previous_articles:
        previous_titles = []
        for prev in previous_articles:
            prev_title = clean_text_for_json(prev.get('title', ''))
            if prev_title:
                previous_titles.append(prev_title)
        
        if previous_titles:
            previous_context = f"""
IMPORTANT - PREVIOUS ARTICLES TO AVOID DUPLICATING:
These articles were already published in recent digests. Do NOT select stories that are:
1. The same event already covered
2. Minor updates to these stories (unless major new development)
3. Similar announcements from the same companies/countries

Previous articles:
{json.dumps(previous_titles, indent=2)}

Rule: If a story is a continuation of something above, it must have MAJOR new developments to be selected.
For example:
- If "Company X announces layoffs" was published, don't select "Company X confirms layoff details"
- If "Country Y sanctions Country Z" was published, don't select "Country Y maintains sanctions"
- But DO select if it's a major escalation: "Country Y declares war on Country Z"
"""
    
    prompt = f"""You are an expert global news curator selecting exactly 10 stories from the provided list for a worldwide audience. Your mission: pick only the most significant, high-impact events that shape the world.

{previous_context}

SELECTION CRITERIA (strict priority order)

1. Mass Impact Test
Would this story directly affect or genuinely interest at least 100 million people worldwide?
If no → reject it.

2. Shareability Test
Is it compelling enough that someone would interrupt a conversation to share it?
If it's just "interesting," reject it — it must be "you NEED to know this."

3. Global Relevance
❌ No single-person stories (medical issues, personal crimes, isolated incidents)
❌ No nostalgic company anniversaries unless impacting millions now
❌ No regional news without a clear worldwide implication
✅ Yes to geopolitical shifts, major economic moves, tech/science breakthroughs, climate disasters, global security threats

4. Novelty & Development Filter
❌ Exclude repetitive crisis/wartime toll updates unless:
- It marks the highest casualty/disaster level in months/years
- It triggers a major political/military/diplomatic shift
- It causes new international action (sanctions, aid missions, peace talks)
Stories must represent a development, escalation, or turning point, not just continuation.

5. DUPLICATE PREVENTION
❌ Do NOT select stories that were covered in previous digests
❌ Avoid minor updates to previously covered events
✅ Only select if there's a MAJOR new development worth reporting

6. Category Balance (flexible, based on quality)
- 4–5 General News: wars, summits, major policy changes, climate events
- 2–3 Business/Economy: trillion-dollar deals, market crashes, industry disruptions
- 2–3 Science/Technology: breakthroughs affecting humanity at scale

REJECTION TRIGGERS
Immediately reject stories that are:
- Individual medical cases or personal mishaps
- Historical/corporate nostalgia without mass impact
- Trivia/fun facts with no real consequences
- Local crimes/incidents unless showing a global trend
- Minor corporate changes (e.g., personality tweaks to AI models)
- Ongoing events without any new development or consequence
- Duplicates or minor updates of previously published articles

Final Rule: Select exactly 10 stories that clear all filters and maximize global importance + novelty.

IMPORTANT: Return ONLY valid JSON with the 10 selected articles.

Return this EXACT structure:
{{
  "selected_articles": [
    {{
      "id": 0,
      "title": "exact title here",
      "url": "exact url here",
      "category": "General News/Business News/Science and Technology News",
      "selection_reason": "Brief reason why this was selected (1-2 sentences)",
      "is_update": false,
      "previous_context": "If this updates a previous story, mention what's new"
    }}
  ]
}}

You must select EXACTLY 10 articles. Include the category for each based on its content.

ARTICLES TO EVALUATE ({len(formatted_articles)} total):
{json.dumps(formatted_articles, indent=2)}"""
    
    return prompt

def select_top_articles_with_ai(articles, previous_articles=None):
    """Use Claude AI to select the top 10 most important articles"""
    print("\n🤖 Using AI to select top 10 most important global news stories...")
    
    if previous_articles:
        print(f"📋 Considering {len(previous_articles)} previous articles to avoid duplicates")
    
    print(f"📋 Evaluating {len(articles)} articles for global impact and relevance...")
    
    if len(articles) > 150:
        print(f"📦 Large article set detected. Processing in stages...")
        
        batch_size = 100
        stage1_selected = []
        
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(articles) + batch_size - 1) // batch_size
            
            print(f"\n🔍 Stage 1 - Batch {batch_num}/{total_batches}: Evaluating {len(batch)} articles")
            
            selection_prompt = create_selection_prompt(batch, previous_articles)
            response = call_claude_api_with_model(
                selection_prompt, 
                f"Selecting top articles from batch {batch_num}",
                CLAUDE_MODEL
            )
            
            if response:
                parsed = parse_json_with_fallback(response)
                if parsed and 'selected_articles' in parsed:
                    stage1_selected.extend(parsed['selected_articles'])
                    print(f"   ✅ Selected {len(parsed['selected_articles'])} articles from this batch")
                else:
                    print(f"   ⚠️ Failed to parse selection for batch {batch_num}")
            else:
                print(f"   ⚠️ Failed to get AI selection for batch {batch_num}")
            
            if batch_num < total_batches:
                time.sleep(2)
        
        if len(stage1_selected) > 10:
            print(f"\n🎯 Stage 2 - Final selection: Choosing top 10 from {len(stage1_selected)} candidates")
            
            final_candidates = []
            for selected in stage1_selected:
                for orig in articles:
                    if orig.get('title') == selected.get('title'):
                        final_candidates.append(orig)
                        break
            
            final_prompt = create_selection_prompt(final_candidates, previous_articles)
            final_response = call_claude_api_with_model(
                final_prompt,
                "Making final selection of top 10 articles",
                CLAUDE_MODEL
            )
            
            if final_response:
                parsed = parse_json_with_fallback(final_response)
                if parsed and 'selected_articles' in parsed:
                    return parsed['selected_articles']
            
            return stage1_selected[:10]
        else:
            return stage1_selected
    
    else:
        selection_prompt = create_selection_prompt(articles, previous_articles)
        response = call_claude_api_with_model(
            selection_prompt,
            "Selecting top 10 most important global news stories",
            CLAUDE_MODEL
        )
        
        if response:
            parsed = parse_json_with_fallback(response)
            if parsed and 'selected_articles' in parsed:
                selected = parsed['selected_articles']
                print(f"✅ AI selected {len(selected)} top stories")
                
                print("\n📌 Selection Overview:")
                for i, article in enumerate(selected[:3], 1):
                    title_preview = article['title'][:60]
                    if len(article['title']) > 60:
                        title_preview += "..."
                    print(f"  {i}. {title_preview}")
                    print(f"     Reason: {article.get('selection_reason', 'High global impact')}")
                    if article.get('is_update'):
                        print(f"     Update: {article.get('previous_context', 'Continues previous story')}")
                
                return selected
        
        return None

def scrape_article_content(url):
    """Scrape full article content from URL with improved error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code != 200:
            print(f"   ⚠️ HTTP {response.status_code} for {url[:50]}...")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        article_text = ""
        
        selectors = [
            'article',
            '[class*="article-body"]',
            '[class*="story-body"]',
            '[class*="content-body"]',
            '[class*="post-content"]',
            '[class*="entry-content"]',
            '[class*="article-content"]',
            '[class*="story-content"]',
            '[class*="main-content"]',
            '[itemprop="articleBody"]',
            'main',
            '[role="main"]',
            '.content',
            '#content'
        ]
        
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                article_text = content.get_text(separator=' ', strip=True)
                if len(article_text) > 200:
                    break
        
        if len(article_text) < 200:
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        article_text = re.sub(r'\s+', ' ', article_text)
        article_text = article_text.strip()
        
        if article_text:
            return article_text[:2000]
        
        return None
        
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout scraping {url[:50]}...")
        return None
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request error scraping {url[:50]}...: {str(e)[:50]}")
        return None
    except Exception as e:
        print(f"   ❌ Error scraping {url[:50]}...: {str(e)[:50]}")
        return None

def create_rewriting_prompt(articles_with_content, previous_articles=None):
    """Create prompt for Claude to rewrite articles in B2 English"""
    
    previous_context = ""
    if previous_articles:
        previous_summaries = []
        for prev in previous_articles[:5]:
            if prev.get('title') and prev.get('summary'):
                previous_summaries.append({
                    'title': clean_text_for_json(prev['title']),
                    'summary': clean_text_for_json(prev['summary'])
                })
        
        if previous_summaries:
            previous_context = f"""
PREVIOUS COVERAGE CONTEXT:
These stories were covered in recent digests. If any of today's articles relate to these, mention it's an update/development:
{json.dumps(previous_summaries, indent=2)}

RULE: If writing about a development of a previous story, start with phrases like:
- "In a major development..."
- "Following yesterday's announcement..."
- "The situation has escalated..."
- "New information reveals..."
"""
    
    prompt = f"""You are the senior news editor for Tennews.org. Today is {datetime.now().strftime('%B %d, %Y')}.

{previous_context}

TASK: Rewrite each article following these STRICT rules:

TITLE RULES:
- Create attractive, engaging headline (8-12 words)
- Add ONE relevant emoji at the beginning
- NEVER copy the original title - always create new
- Use B2 level English (intermediate)
- If it's an update to a previous story, reflect that it's new development

BODY TEXT RULES:
- Write EXACTLY 40-50 words
- Use B2 level English
- Explain technical terms in parentheses immediately
- Include the most important information
- Make it complete despite length limit
- If updating previous story, mention what's new/different

Return ONLY valid JSON:
{{
  "digest_date": "{datetime.now().strftime('%B %d, %Y')}",
  "generation_time": "{datetime.now().strftime('%I:%M %p UTC')}",
  "articles": [
    {{
      "rank": 1,
      "emoji": "🌍",
      "title": "New engaging title without emoji here",
      "summary": "40-50 word B2 English summary with technical terms explained in parentheses",
      "category": "Category here",
      "importance": "High/Critical/Major",
      "source": "Reuters",
      "date": "{datetime.now().strftime('%B %d, %Y')}",
      "url": "Original URL here",
      "is_update": false,
      "update_context": "If updating previous story, brief note about what's new"
    }}
  ]
}}

ARTICLES TO REWRITE:
"""
    
    for i, article in enumerate(articles_with_content, 1):
        content = clean_text_for_json(article.get('content', 'No content available'))
        if len(content) > 500:
            content = content[:500] + "..."
            
        prompt += f"""
ARTICLE {i}:
Original Title: {clean_text_for_json(article['title'])}
Category: {article['category']}
Why Selected: {article.get('selection_reason', 'Important global news')}
Is Update: {article.get('is_update', False)}
Previous Context: {article.get('previous_context', 'N/A')}
Source: {article['source']}
URL: {article['url']}
Content: {content}

---"""
    
    prompt += "\n\nReturn ONLY the JSON with all 10 rewritten articles. Set importance based on the selection reason."
    
    return prompt

def deduplicate_with_claude(articles):
    """Use Claude Sonnet 3.5 to identify and remove duplicate news stories"""
    if not articles:
        return articles
    
    print(f"\n🤖 Using Claude Sonnet 3.5 to identify duplicate news stories...")
    print(f"📋 Analyzing {len(articles)} articles for duplicates...")
    
    batch_size = 100
    if len(articles) > batch_size:
        all_deduplicated = []
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            print(f"\n📦 Processing deduplication batch {i//batch_size + 1}/{(len(articles) + batch_size - 1)//batch_size}")
            
            deduplicated_batch = process_deduplication_batch(batch)
            if deduplicated_batch:
                all_deduplicated.extend(deduplicated_batch)
            
            time.sleep(1)
        
        return all_deduplicated
    else:
        return process_deduplication_batch(articles)

def process_deduplication_batch(articles):
    """Process a single batch of articles for deduplication"""
    formatted_articles = []
    for i, article in enumerate(articles):
        formatted_articles.append({
            "id": i,
            "title": clean_text_for_json(article.get('title', '')),
            "url": article.get('url', ''),
            "domain": article.get('domain', '')
        })
    
    prompt = f"""You are a news editor identifying duplicate news stories.

TASK: Group articles about the SAME NEWS EVENT and select the BEST title from each group.

RULES:
1. Articles are duplicates if they report the SAME SPECIFIC EVENT (not just same topic)
2. From each duplicate group, choose the article with the MOST INTERESTING and CATCHY title
3. Keep ALL unique stories (stories that have no duplicates)
4. Be strict - only group EXACT same events, not similar topics

Return ONLY valid JSON with this structure:
{{
  "unique_articles": [
    {{
      "id": 0,
      "reason": "Selected because: best title among 3 duplicates about X event"
    }},
    {{
      "id": 5,
      "reason": "Unique story - no duplicates found"
    }}
  ]
}}

IMPORTANT: Return the ID of EVERY article you want to keep (both unique stories and best titles from duplicate groups).

ARTICLES TO ANALYZE:
{json.dumps(formatted_articles, indent=2)}"""
    
    response = call_claude_api_with_model(prompt, "Identifying duplicate news stories", CLAUDE_SONNET_MODEL)
    
    if not response:
        print("⚠️ Deduplication failed, keeping all articles")
        return articles
    
    try:
        parsed_data = parse_json_with_fallback(response)
        if not parsed_data or 'unique_articles' not in parsed_data:
            print("⚠️ Failed to parse deduplication results, keeping all articles")
            return articles
        
        ids_to_keep = set()
        reasons = {}
        for item in parsed_data['unique_articles']:
            article_id = item.get('id')
            if article_id is not None:
                ids_to_keep.add(article_id)
                reasons[article_id] = item.get('reason', '')
        
        deduplicated_articles = []
        duplicate_count = 0
        
        for i, article in enumerate(articles):
            if i in ids_to_keep:
                deduplicated_articles.append(article)
            else:
                duplicate_count += 1
        
        print(f"✅ Deduplication complete:")
        print(f"   - Original articles: {len(articles)}")
        print(f"   - Duplicates removed: {duplicate_count}")
        print(f"   - Unique articles kept: {len(deduplicated_articles)}")
        
        if len(reasons) > 0 and len(deduplicated_articles) > 0:
            print("\n📌 Sample decisions:")
            sample_count = min(3, len(reasons))
            for i, (aid, reason) in enumerate(list(reasons.items())[:sample_count]):
                if aid < len(articles):
                    title_preview = articles[aid]['title'][:60]
                    if len(articles[aid]['title']) > 60:
                        title_preview += "..."
                    print(f"   - Kept: {title_preview}")
                    print(f"     Reason: {reason}")
        
        return deduplicated_articles
        
    except Exception as e:
        print(f"⚠️ Error in deduplication: {str(e)[:100]}")
        return articles

def call_claude_api_with_model(prompt, task_description, model=None):
    """Generic Claude API call function with model selection and improved error handling"""
    if not CLAUDE_API_KEY or CLAUDE_API_KEY == "your-api-key-here-for-testing":
        print("\n❌ ERROR: No valid API key set!")
        print("Please set your Claude API key in GitHub Secrets")
        return None
    
    api_model = model if model else CLAUDE_MODEL
        
    print(f"\n🤖 {task_description}...")
    print(f"   Using model: {api_model}")
    
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    max_tokens = 4000 if "scoring" in task_description.lower() else 8000
    
    data = {
        "model": api_model,
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            timeout_seconds = 120 if "scoring" in task_description.lower() else 90
            response = requests.post(url, headers=headers, json=data, timeout=timeout_seconds)
            
            if response.status_code == 200:
                result = response.json()
                if 'content' in result and len(result['content']) > 0:
                    print(f"✅ {task_description} complete!")
                    return result['content'][0]['text']
                else:
                    print(f"❌ Unexpected response structure")
                    return None
                    
            elif response.status_code == 401:
                print("❌ Authentication error - check your API key")
                return None
            elif response.status_code == 404:
                print(f"❌ Model not found: {api_model}")
                return None
            elif response.status_code == 429:
                wait_time = min(30, 2 ** attempt * 3)
                print(f"⚠️ Rate limited, waiting {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            elif response.status_code == 529:
                if attempt < max_retries - 1:
                    wait_time = 30 + (attempt * 10)
                    print(f"⚠️ Claude is overloaded. Waiting {wait_time} seconds before retry... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print("❌ Claude is temporarily overloaded. Please try again in a few minutes.")
                    return None
            elif response.status_code == 500:
                wait_time = min(20, 2 ** attempt * 3)
                print(f"⚠️ Server error, retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                error_text = response.text[:200] if response.text else "No error message"
                print(f"❌ Error {response.status_code}: {error_text}")
                if attempt < max_retries - 1 and response.status_code >= 500:
                    wait_time = 10
                    print(f"   Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                return None
                
        except requests.exceptions.Timeout:
            print(f"⚠️ Request timed out after {timeout_seconds} seconds (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                wait_time = 5 + (attempt * 5)
                print(f"   Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            return None
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Connection error (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                wait_time = 5 + (attempt * 3)
                print(f"   Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)[:100]}")
            if attempt < max_retries - 1:
                wait_time = 5
                print(f"⚠️ Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            return None
    
    print(f"❌ Failed after {max_retries} attempts")
    return None

def call_claude_api(prompt, task_description):
    """Generic Claude API call function with better error handling"""
    return call_claude_api_with_model(prompt, task_description, CLAUDE_MODEL)

def parse_json_with_fallback(response_text):
    """Parse JSON with multiple fallback strategies and improved error handling"""
    if not response_text:
        print("⚠️ Empty response text")
        return None
        
    response_text = response_text.strip()
    
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        error_msg = str(e)
        if "Extra data" in error_msg:
            try:
                brace_count = 0
                in_string = False
                escape_next = False
                
                for i, char in enumerate(response_text):
                    if escape_next:
                        escape_next = False
                        continue
                        
                    if char == '\\' and not escape_next:
                        escape_next = True
                        continue
                        
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                        
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                first_json = response_text[:i+1]
                                return json.loads(first_json)
            except Exception as inner_e:
                print(f"⚠️ Failed to extract first JSON object: {str(inner_e)[:50]}")
        
        print(f"⚠️ Initial JSON parse failed: {error_msg[:100]}")
    
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
    except Exception as e:
        print(f"⚠️ JSON boundary extraction failed: {str(e)[:50]}")
    
    try:
        fixed_text = response_text
        fixed_text = fixed_text.replace('"', '"').replace('"', '"')
        fixed_text = fixed_text.replace(''', "'").replace(''', "'")
        fixed_text = fixed_text.replace('–', '-').replace('—', '-')
        
        return json.loads(fixed_text)
    except Exception as e:
        print(f"⚠️ Smart quote fix failed: {str(e)[:50]}")
    
    try:
        if '[' in response_text:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    return {"scored_articles": parsed}
                return parsed
    except Exception as e:
        print(f"⚠️ Array extraction failed: {str(e)[:50]}")
    
    print("❌ All JSON parsing attempts failed")
    return None

def fallback_selection(articles):
    """Fallback method to select articles if AI selection fails"""
    print("\n📊 Using fallback selection method...")
    
    selected = []
    seen_titles = set()
    
    for article in articles:
        title = article.get('title', '').lower()
        if title and title not in seen_titles:
            seen_titles.add(title)
            selected.append({
                'id': len(selected),
                'title': article['title'],
                'url': article['url'],
                'category': detect_article_category(article),
                'selection_reason': 'Selected via fallback method',
                'is_update': False,
                'previous_context': ''
            })
            
            if len(selected) >= 10:
                break
    
    return selected

# ==================== MAIN EXECUTION ====================
def main():
    """Main execution function"""
    print("🚀 TENNEWS DAILY DIGEST - GITHUB VERSION")
    print("📊 Using AI to select the most important global news")
    print("=" * 70)
    
    # Initialize Excel file
    initialize_excel_file()
    
    # Check API key
    if not CLAUDE_API_KEY or CLAUDE_API_KEY == "your-api-key-here-for-testing":
        print("\n❌ ERROR: No valid Claude API key found!")
        return
    
    try:
        # Create public directory if it doesn't exist
        os.makedirs('public', exist_ok=True)
        
        # PHASE 1: Fetch previous articles from Excel
        previous_articles = fetch_previous_articles_from_excel()
        
        # PHASE 2: Fetch news from GDELT
        articles = fetch_gdelt_news_last_24_hours()
        
        if not articles:
            print("\n❌ No articles found!")
            return
        
        # PHASE 3: Deduplicate
        unique_articles = deduplicate_articles(articles)
        
        if not unique_articles:
            print("\n❌ No articles from approved sources found!")
            return
        
        # PHASE 3.5: Use Claude Sonnet to remove duplicate news stories
        deduplicated_articles = deduplicate_with_claude(unique_articles)
        
        if not deduplicated_articles:
            print("\n❌ No articles remaining after deduplication!")
            return
        
        # PHASE 5: AI Selection of top 10 articles
        print("\n📊 Preparing articles for AI selection...")
        
        selected_articles = select_top_articles_with_ai(deduplicated_articles, previous_articles)
        
        if not selected_articles:
            print("\n⚠️ AI selection failed, trying fallback method...")
            selected_articles = fallback_selection(deduplicated_articles)
            
            if not selected_articles:
                print("\n❌ Failed to select articles even with fallback method")
                return
        
        if len(selected_articles) > 10:
            selected_articles = selected_articles[:10]
            print(f"📋 Trimmed to exactly 10 articles")
        elif len(selected_articles) < 10:
            print(f"⚠️ Only {len(selected_articles)} articles selected (target was 10)")
        
        print(f"\n✅ Selected {len(selected_articles)} top articles for the digest")
        
        print("\n📰 Selected Articles:")
        for i, article in enumerate(selected_articles, 1):
            title_preview = article['title'][:60]
            if len(article['title']) > 60:
                title_preview += "..."
            print(f"  {i}. {title_preview}")
            print(f"     Category: {article.get('category', 'General News')}")
        
        top_10_articles = selected_articles
        
        # PHASE 6: Fetch full content for top 10
        print("\n🌐 Fetching full content for top 10 articles...")
        
        articles_with_content = []
        for i, article in enumerate(top_10_articles, 1):
            title_preview = article['title'][:60]
            if len(article['title']) > 60:
                title_preview += "..."
            print(f"\n📄 Fetching article {i}/10: {title_preview}")
            
            content = scrape_article_content(article['url'])
            
            if content:
                print(f"   ✓ Retrieved {len(content)} characters")
            else:
                print(f"   ⚠️ Using title only (scraping failed)")
                content = article['title']
            
            try:
                url_parts = article['url'].split('/')
                if len(url_parts) >= 3:
                    domain = url_parts[2].replace('www.', '')
                else:
                    domain = 'Unknown'
            except:
                domain = 'Unknown'
            
            source_map = {
                'cnn.com': 'CNN',
                'bbc.com': 'BBC',
                'bbc.co.uk': 'BBC',
                'reuters.com': 'Reuters',
                'apnews.com': 'Associated Press',
                'theguardian.com': 'The Guardian',
                'nytimes.com': 'The New York Times',
                'bloomberg.com': 'Bloomberg',
                'washingtonpost.com': 'The Washington Post',
                'wsj.com': 'The Wall Street Journal',
                'foxnews.com': 'Fox News',
                'cnbc.com': 'CNBC',
                'npr.org': 'NPR',
                'aljazeera.com': 'Al Jazeera',
                'france24.com': 'France 24',
                'scmp.com': 'South China Morning Post',
                'forbes.com': 'Forbes',
                'techcrunch.com': 'TechCrunch',
                'wired.com': 'Wired',
                'nature.com': 'Nature',
                'science.org': 'Science',
                'ft.com': 'Financial Times',
                'politico.com': 'Politico',
                'politico.eu': 'Politico Europe',
                'axios.com': 'Axios',
                'vox.com': 'Vox',
                'thehill.com': 'The Hill',
                'time.com': 'TIME',
                'newsweek.com': 'Newsweek',
                'usatoday.com': 'USA Today',
                'abcnews.go.com': 'ABC News',
                'nbcnews.com': 'NBC News',
                'cbsnews.com': 'CBS News',
                'msnbc.com': 'MSNBC',
                'marketwatch.com': 'MarketWatch',
                'businessinsider.com': 'Business Insider',
                'fortune.com': 'Fortune',
                'economist.com': 'The Economist',
                'barrons.com': 'Barron\'s'
            }
            source = source_map.get(domain, domain.replace('.com', '').replace('.org', '').replace('.net', '').replace('.co.uk', '').title())
            
            article_data = article.copy()
            article_data['content'] = content
            article_data['source'] = source
            articles_with_content.append(article_data)
        
        # PHASE 7: Rewrite articles
        print("\n✍️ Creating B2 English summaries...")
        rewriting_prompt = create_rewriting_prompt(articles_with_content, previous_articles)
        
        final_response = call_claude_api(rewriting_prompt, "Rewriting articles in B2 English")
        
        if not final_response:
            print("\n❌ Failed to rewrite articles")
            return
        
        articles_data = parse_json_with_fallback(final_response)
        if not articles_data:
            print("\n❌ Failed to parse final response")
            return
        
        if 'articles' not in articles_data or not articles_data['articles']:
            print("\n❌ No articles in final response")
            return
        
        print(f"\n✅ Successfully created final digest with {len(articles_data['articles'])} articles")
        
        # PHASE 8: Generate daily greeting and reading time
        print("\n🎯 Generating daily greeting and reading time...")
        daily_greeting, reading_time = generate_daily_greeting_and_reading_time(articles_data['articles'])
        formatted_date = get_formatted_date()
        
        print(f"📅 Date: {formatted_date}")
        print(f"👋 Greeting: {daily_greeting}")
        print(f"⏱️ Reading time: {reading_time}")
        
        # PHASE 9: Generate historical events for today
        historical_events = generate_historical_events()
        
        # PHASE 10: Save to Excel
        save_articles_to_excel(articles_data, daily_greeting, reading_time, formatted_date)
        
        # PHASE 11: Save to JSON for website
        output_data = {
            'lastUpdate': datetime.now().isoformat(),
            'displayDate': formatted_date,
            'dailyGreeting': daily_greeting,
            'readingTime': reading_time,
            'articles': articles_data['articles'],
            'historicalEvents': historical_events
        }
        
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Successfully generated news digest!")
        print(f"📄 JSON saved to: {OUTPUT_JSON}")
        print(f"📊 Excel archive: {EXCEL_FILE}")
        
        # Show preview
        print("\n📰 DIGEST PREVIEW:")
        print("-" * 70)
        print(f"📅 {formatted_date}")
        print(f"👋 {daily_greeting}")
        print(f"⏱️ {reading_time}")
        print("\n📚 Historical Events for Today:")
        for event in historical_events:
            print(f"   • {event['year']}: {event['description']}")
        print("-" * 70)
        for article in articles_data['articles'][:3]:
            print(f"{article['rank']}. {article['emoji']} {article['title']}")
            print(f"   Impact: {article.get('importance', 'High')}")
            summary_preview = article['summary'][:80]
            if len(article['summary']) > 80:
                summary_preview += "..."
            print(f"   {summary_preview}")
            print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error in main execution: {str(e)}")
        import traceback
        print("\nFull error traceback:")
        traceback.print_exc()
        return

# ==================== SCRIPT EXECUTION ====================
if __name__ == "__main__":
    print("Welcome to Tennews Daily Digest - GitHub Version!")
    print("\nFeatures:")
    print("✓ AI-powered selection of top 10 global news")
    print("✓ Strict criteria for global impact and relevance")
    print("✓ Full content retrieval for selected articles")
    print("✓ B2 English summaries (40-50 words)")
    print("✓ Automatic duplicate detection")
    print("✓ Excel archive for previous articles")
    print("✓ JSON output for Next.js website")
    print("\n🔧 Using Claude Opus 4.1 model")
    
    if CLAUDE_API_KEY == "your-api-key-here-for-testing":
        print("\n⚠️ WARNING: Claude API key not set!")
        print("Please set CLAUDE_API_KEY environment variable")
        print("Or add it to GitHub Secrets for automation")
    else:
        print("\n✅ API key detected!")
        print("\nStarting news generation...")
        main()
