from django.urls import path
from .views import ArtikelListCreateView, ArtikelDetailView, ChatMessageList, ChatMessageDetail, QuizDetailView, QuizListCreateView,  FavoriteListCreateView, FavoriteDeleteView, FavoriteListByUserView, SummaryListCreateView, SummaryDetailView

urlpatterns = [
    path('artikels/', ArtikelListCreateView.as_view(), name='artikel-list'),
    path('artikels/<str:pk>/', ArtikelDetailView.as_view(), name='artikel-detail'),
    path('chats/', ChatMessageList.as_view(), name='chat-list'),
    path('chats/<str:pk>/', ChatMessageDetail.as_view(), name='chat-detail'),
    path('quizzes/', QuizListCreateView.as_view(), name='quiz-list'),
    path('quizzes/<str:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('favorites/', FavoriteListCreateView.as_view()), 
    path('favorites/<str:user_id>/', FavoriteListByUserView.as_view()),  
    path('favorites/delete/<str:pk>/', FavoriteDeleteView.as_view()), 
    path('summaries/', SummaryListCreateView.as_view(), name='summary-list'),
    path('summaries/<str:pk>/', SummaryDetailView.as_view(), name='summary-detail'),
]
