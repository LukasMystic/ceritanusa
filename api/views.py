from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Artikel, ChatMessage, Quiz, Favorite, Summary
from .serializers import ArtikelSerializer, ChatMessageSerializer, QuizSerializer, FavoriteSerializer, SummarySerializer
from mongoengine.errors import DoesNotExist, ValidationError
from rest_framework import viewsets
from .summarizer import summarize_text

# Articles
class ArtikelListCreateView(APIView):
    def get(self, request):
        artikels = Artikel.objects()
        serializer = ArtikelSerializer(artikels, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArtikelSerializer(data=request.data)
        if serializer.is_valid():
            artikel = Artikel(**serializer.validated_data)
            artikel.save()
            return Response(ArtikelSerializer(artikel).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArtikelDetailView(APIView):
    def get_object(self, pk):
        try:
            return Artikel.objects.get(id=pk)
        except (DoesNotExist, ValidationError):
            return None

    def get(self, request, pk):
        artikel = self.get_object(pk)
        if not artikel:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ArtikelSerializer(artikel).data)

    def put(self, request, pk):
        artikel = self.get_object(pk)
        if not artikel:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ArtikelSerializer(data=request.data)
        if serializer.is_valid():
            for key, value in serializer.validated_data.items():
                setattr(artikel, key, value)
            artikel.save()
            return Response(ArtikelSerializer(artikel).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        artikel = self.get_object(pk)
        if not artikel:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        artikel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Chatting
class ChatMessageList(APIView):
    def get(self, request):
        messages = ChatMessage.objects.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatMessageDetail(APIView):
    def get(self, request, pk):
        try:
            message = ChatMessage.objects.get(id=pk)
        except ChatMessage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ChatMessageSerializer(message)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            message = ChatMessage.objects.get(id=pk)
        except ChatMessage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ChatMessageSerializer(message, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            message = ChatMessage.objects.get(id=pk)
            message.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ChatMessage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
# QUiz
class QuizListCreateView(APIView):
    def get(self, request):
        quizzes = Quiz.objects()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizDetailView(APIView):
    def get_object(self, pk):
        try:
            return Quiz.objects.get(id=pk)
        except DoesNotExist:
            return None

    def get(self, request, pk):
        quiz = self.get_object(pk)
        if not quiz:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)

    def put(self, request, pk):
        quiz = self.get_object(pk)
        if not quiz:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuizSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        quiz = self.get_object(pk)
        if not quiz:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# Favourite
class FavoriteListCreateView(APIView):
    def post(self, request):
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Article added to favorites"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FavoriteListByUserView(APIView):
    def get(self, request, user_id):
        favorites = Favorite.objects(user_id=user_id)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

class FavoriteDeleteView(APIView):
    def delete(self, request, pk):
        try:
            favorite = Favorite.objects.get(id=pk)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
# Summarizer


class SummaryListCreateView(APIView):
    def get(self, request):
        summaries = Summary.objects()
        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SummarySerializer(data=request.data)
        if serializer.is_valid():
            summary = serializer.save()
            return Response(SummarySerializer(summary).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SummaryDetailView(APIView):
    def get(self, request, pk):
        try:
            summary = Summary.objects.get(id=pk)
        except Summary.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SummarySerializer(summary)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            summary = Summary.objects.get(id=pk)
        except Summary.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SummarySerializer(summary, data=request.data, partial=True)
        if serializer.is_valid():
            updated_summary = serializer.save()
            return Response(SummarySerializer(updated_summary).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            summary = Summary.objects.get(id=pk)
            summary.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Summary.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)