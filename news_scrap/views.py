from django.shortcuts import render
from .models import *
import httpx
import json
from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import heapq
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from .serializer import *
from rest_framework.response import *
from rest_framework.renderers import *
from rest_framework.decorators import *
import re

load_dotenv()
nltk.download("punkt")
nltk.download("stopwords")

# Function for retrieving news from previous days
@csrf_exempt
@api_view(['GET'])
def getNewsForDay(request, day): # Day should be yyyymmdd
    if request.method == "GET":
        news = get_news_from_db(day=day)
        if (news is None) or not news:
            topics = get_topic_from_gtrend(day=day)     # List of topics
            articles = get_articles_about_topic(list_of_topic=topics)   # List of articles about topics [{"title" : "  ", "topic" : " " , "url" : " ", "url_image" : " "}]

            articles_summary = {}
            topic_source = {}
            topic_image_url = {}
            topic_news = []
            
            for article in articles:
                current_topic = article["topic"]
                if (current_topic in articles_summary):
                    articles_summary[current_topic].append(summarize_news(article['url'], None))
                    source_obj = Sources.objects.create(url=article['url'], title=article['title'])
                    topic_source[current_topic].append(source_obj)
                    source_obj.save()
                else:
                    topic_image_url[current_topic] = article["image_url"]
                    articles_summary[current_topic] = [summarize_news(article['url'], None)]
                    source_obj = Sources.objects.create(url=article['url'], title=article['title'])
                    topic_source[current_topic] = [source_obj]
                    source_obj.save()

            for topic in articles_summary:
                json_structured = {}
                json_structured["title"] = topic
                json_structured["image_url"] = topic_image_url[topic]
                json_structured["content"] = summarize_all_news(articles=articles_summary[topic])
                news_obj = News.objects.create(
                    title=topic,
                    content=json_structured["content"],
                    day=day,
                    image_url = topic_image_url[topic]
                )
                news_obj.sources.set(topic_source[topic])
                news_obj.save()
                json_structured["day"] = day
                topic_news.append(json_structured)

            final_result = {"news":topic_news}
            return JsonResponse(final_result)
        
        else :
            result = {}
            arr_result = []
            for n in news:
                serializer = NewsSerializer(n)
                arr_result.append(serializer.data)
            result["news"] = arr_result
            return JsonResponse(result)
    else:
        pass        

def get_news_desc(request, day):
    if request.method == "GET":
        news = get_topic_from_gtrend(day=day)
        return HttpResponse(news)

def get_news_from_db(day):
    try:
        news = News.objects.filter(day = int(day))
        return news
    except ObjectDoesNotExist:
        return None

@api_view(['GET'])
def get_news_by_title(request, title):
    try:
        news = News.objects.get(title=title)
        serializer = NewsSerializer(news)
        json_data = serializer.data
        return JsonResponse(json_data)
    except ObjectDoesNotExist:
        return JsonResponse({"message" : "News doesn't exist"})
 
def get_topic_from_gtrend(day):
    result = []
    res = httpx.get(f"https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-420&ed={day}&geo=US&hl=en-US&ns=15")
    data = json.loads(res.text.replace(")]}',", ""))
    counter = 0
    for dt in data["default"]["trendingSearchesDays"][0]["trendingSearches"]:
        if counter < 3:
            obj = {
                "topic": dt["title"]["query"],
                }
            result.append(obj)
            counter += 1
    return result


def get_articles_about_topic(list_of_topic):
    news_api_result = []
    newsapi = NewsApiClient(api_key=os.getenv('API_KEY'))
    for topic in list_of_topic:
        data = newsapi.get_everything(q=topic["topic"])
        articles = data["articles"]
        if data["totalResults"] > 7:
            for i in range(3):
                obj = {
                    "title" : articles[i]["title"],
                    "url" : articles[i]["url"],
                    "topic" : topic["topic"],
                    "image_url" : articles[i]["urlToImage"]
                }
                news_api_result.append(obj)
        else :
            for i in articles:
                obj = {
                    "title" : i["title"],
                    "url" : i["url"],
                    "topic" : topic["topic"],
                    "image_url" : articles[i]["urlToImage"]
                }
                news_api_result.append(obj)
    return news_api_result

def summarize_news(url, article_text):
    if(url is not None):
    #Fetch the page
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        #Assuming the article is in a <p> tag
        article_text = '\n'.join([p.text for p in soup.find_all('p')])
    else:
        article_text = article_text

    words = word_tokenize(article_text)
    
    # Creating a frequency table to keep the score of each word
    freq_table = dict()
    for word in words:
        word = word.lower()
        if word in stopwords.words('english'):
            continue
        if word in freq_table:
            freq_table[word] += 1
        else:
            freq_table[word] = 1
    
    # Tokenizing the sentences
    sentences = sent_tokenize(article_text)
    
    # Scoring each sentence
    sentence_scores = dict()
    for sentence in sentences:
        for word, freq in freq_table.items():
            if word in sentence.lower():
                if sentence in sentence_scores:
                    sentence_scores[sentence] += freq
                else:
                    sentence_scores[sentence] = freq
    
    # Getting the summary
    summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    
    return summary


def summarize_all_news(articles):
    merged_article = ''.join([article for article in articles])
    return summarize_news(None, merged_article)

def home(request):
    return HttpResponse("Hello")
        
def remove_unwanted_chars(text):
    # Remove HTML tags
    clean_text = re.sub(r'<.*?>', '', text)
    
    # Remove newline characters (\n)
    clean_text = clean_text.replace('\n', '')
    
    # Remove Unicode escape sequences (\uXXXX)
    clean_text = clean_text.encode('ascii', 'ignore').decode()
    
    return clean_text

def tes_remove(request):
    text = News.objects.get(title="Trump shoes")
    clean_text = remove_unwanted_chars(text.content)
    return HttpResponse(clean_text)


def render_all_news(request):
    try :
        for i in range(20240217, 20240228):
            getNewsForDay(request, i)
        return HttpResponse("Succedd")
    except Exception as e:
        return f"Error : {e}"