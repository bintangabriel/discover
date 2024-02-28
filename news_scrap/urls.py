from django.urls import path
from . import views

urlpatterns = [
    path('<str:day>', views.getNewsForDay),
    path('', views.home),
    path('<str:day>/full', views.get_news_desc),
    path('full/<str:title>', views.get_news_by_title),
    path('clean/text', views.tes_remove),
    path('first-news/render', views.render_all_news)
]