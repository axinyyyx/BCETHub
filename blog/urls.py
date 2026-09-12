from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('live-search', views.live_search, name="live_search"),
    path('search', views.search, name="search"),
    path('routine', views.routine, name="routine"),
    path('notes', views.notes, name="notes"),
    path('induction', views.induction, name="induction"),
    path('mess-menu', views.mess_menu, name="mess_menu"),
    path('about', views.about, name="about"),
    path('attendance/', views.pooling_page, name='pooling_page'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/live/', views.live_counter, name='live_counter'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('qr-code', views.qr_code, name='qr_code'),
]