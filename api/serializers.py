from rest_framework import serializers
from .models import ChatMessage
from .models import Artikel, Quiz, Question, Choice, Favorite, Summary
from datetime import datetime

class ArtikelSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    image = serializers.FileField(required=False, allow_null=True)  # Optional

    def create(self, validated_data):
        return Artikel(**validated_data).save()

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()
        return instance

class ChatMessageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    sender = serializers.CharField()
    receiver = serializers.CharField()
    message = serializers.CharField()
    timestamp = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return ChatMessage(**validated_data).save()

    def update(self, instance, validated_data):
        instance.sender = validated_data.get('sender', instance.sender)
        instance.receiver = validated_data.get('receiver', instance.receiver)
        instance.message = validated_data.get('message', instance.message)
        instance.save()
        return instance


class ChoiceSerializer(serializers.Serializer):
    text = serializers.CharField()
    is_correct = serializers.BooleanField()

class QuestionSerializer(serializers.Serializer):
    text = serializers.CharField()
    image = serializers.ImageField(required=False, allow_null=True)
    choices = ChoiceSerializer(many=True)

class QuizSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField()
    questions = QuestionSerializer(many=True)
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        questions = []
        for q in questions_data:
            choices = [Choice(**c) for c in q['choices']]
            questions.append(Question(text=q['text'], image=q.get('image'), choices=choices))
        quiz = Quiz(**validated_data, questions=questions)
        quiz.save()
        return quiz

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        questions_data = validated_data.get('questions')
        if questions_data:
            questions = []
            for q in questions_data:
                choices = [Choice(**c) for c in q['choices']]
                questions.append(Question(text=q['text'], image=q.get('image'), choices=choices))
            instance.questions = questions

        instance.save()
        return instance
    
class FavoriteSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField()
    article_id = serializers.CharField()

    def create(self, validated_data):
        return Favorite.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.article_id = validated_data.get('article_id', instance.article_id)
        instance.save()
        return instance

class SummarySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    original_text = serializers.CharField()
    summarized_text = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        from .summarizer import summarize_text  # import the summarizer function

        text = validated_data['original_text']
        summary = summarize_text(text)

        summary_instance = Summary(
            original_text=text,
            summarized_text=summary
        )
        summary_instance.save()
        return summary_instance

    def update(self, instance, validated_data):
        # Allow updating the summarized_text manually
        instance.summarized_text = validated_data.get('summarized_text', instance.summarized_text)
        instance.updated_at = datetime.utcnow()
        instance.save()
        return instance