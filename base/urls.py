from django.urls import path
from .views import *
from . import views
urlpatterns = [
    path('glucose_reading/', glucose_reading_list, name='glucose_reading_list'),
    path('previous_readings/', previous_readings, name='previous_readings'), 
    path('glucose_graph/<str:reading_type>/', glucose_reading_graph, name='glucose_graph'),
    path('glucose_graph/', glucose_reading_graph, {'reading_type': 'all'}, name='glucose_graph_all'),
    path('glucose_reading_success/', glucose_reading_success, name='glucose_reading_success'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('view_meal_plan/', view_meal_plan, name='view_meal_plan'),
    path('chatbot/', chatbot, name='chatbot'),
    path('', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    # Other paths...
]
