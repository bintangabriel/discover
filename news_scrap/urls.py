from django.urls import path
from . import views

urlpatterns = [
    path('<str:day>', views.getNewsForDay),
    path('', views.home),
    path('<str:day>/full', views.get_news_desc),
    path('full/<str:slug>', views.get_news_by_slug),
    path('clean/text', views.tes_remove),
    path('first-news/render', views.render_all_news),
    path('clean-news/content', views.clean_content_text)
]