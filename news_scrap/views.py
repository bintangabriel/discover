from django.shortcuts import render
from .models import *
import httpx
import json
from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
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

# Function for retrieving news from previous days
@csrf_exempt
@api_view(['GET'])
def getNewsForDay(request, day): # Day should be yyyymmdd
    if request.method == "GET":
        news = get_news_from_db(day=day)
        if not news:
            return JsonResponse({"message": "finished"})
        else:
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
def get_news_by_slug(request, slug):
    try:
        news = News.objects.get(slug=slug)
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
        return HttpResponse("Succeed")
    except Exception as e:
        return f"Error : {e}"
    
def clean_content_text(request):
    all_news = News.objects.all()
    for news in all_news:
        news.content = remove_unwanted_chars(news.content)
        news.save()
    return HttpResponse("Succeed")