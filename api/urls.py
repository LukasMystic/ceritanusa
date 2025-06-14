from django.urls import path
from .views import ArtikelListCreateView, ArtikelDetailView, ChatMessageList, ChatMessageDetail, QuizDetailView, QuizListCreateView,  FavoriteListCreateView, FavoriteDeleteView, FavoriteListByUserView, SummaryListCreateView, SummaryDetailView, ArtikelImageView, ChatOverviewView, SummaryByArticleView, QuizQuestionImageView, QuizListByAuthorView

urlpatterns = [
    path('artikels/', ArtikelListCreateView.as_view(), name='artikel-list'),
    path('artikels/<str:pk>/', ArtikelDetailView.as_view(), name='artikel-detail'),
    path('artikels/<str:pk>/image/', ArtikelImageView.as_view(), name='artikel-image'),
    path('chats/', ChatMessageList.as_view(), name='chat-list'),
    path('chats/<str:pk>/', ChatMessageDetail.as_view(), name='chat-detail'),
    path('chat-overview/<str:uid>/', ChatOverviewView.as_view(), name='chat-overview'),
    path('quizzes/', QuizListCreateView.as_view(), name='quiz-list'),
    path('quizzes/<str:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<str:quiz_id>/questions/<int:question_index>/image/', QuizQuestionImageView.as_view()),
    path('quizzes/by-author/<str:author_id>/', QuizListByAuthorView.as_view(), name='quiz-by-author'),  
    path('favorites/', FavoriteListCreateView.as_view()), 
    path('favorites/<str:user_id>/', FavoriteListByUserView.as_view()),  
    path('favorites/delete/<str:pk>/', FavoriteDeleteView.as_view()), 
    path('summaries/', SummaryListCreateView.as_view(), name='summary-list'),
    path('summaries/<str:pk>/', SummaryDetailView.as_view(), name='summary-detail'),
    path('summaries/by-article/<str:article_id>/', SummaryByArticleView.as_view(), name='summary-by-article'),
    
]
