from django.urls import include, path
from main_app import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('charts/', views.ChartViewSet.as_view()),
    path('scrapped_offers/', views.ScrappedOfferViewSet.as_view()),
    path('executed_tasks/', views.ExecutedTaskViewSet.as_view()),
    path('users/', views.UserViewSet.as_view()),
    path('tasks/', views.PlannedTaskViewSet.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)