from django.urls import path
from Spider.views import PictureSpiderView

urlpatterns = [
    path('Pictures/', PictureSpiderView.as_view(), name="Pictures"),
]