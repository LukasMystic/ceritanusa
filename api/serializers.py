from rest_framework import serializers
from .models import ChatMessage
from .models import Artikel, Quiz, Question, Choice, Favorite, Summary
from datetime import datetime
from .summarizer import summarize_text
from mongoengine import fields
from gridfs import GridFS
from django.core.files.uploadedfile import InMemoryUploadedFile

import mongoengine.connection
fs = GridFS(mongoengine.connection.get_db())


class ArtikelSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    content = serializers.CharField()
    author = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    image = serializers.FileField(required=False, allow_null=True)

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        artikel = Artikel(**validated_data)
        if image:
            artikel.image.put(image, content_type=image.content_type, filename=image.name)
        artikel.save()
        return artikel

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            # Return the image file id or a download URL
            data['image'] = f"/api/artikels/{str(instance.id)}/image/"
        else:
            data['image'] = None
        return data


    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.author = validated_data.get('author', instance.author)
        
        image = validated_data.get('image', None)
        if image:
            instance.image.replace(image, content_type=image.content_type, filename=image.name)

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

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "sender": instance.sender,    # Firestore UID
            "receiver": instance.receiver,
            "message": instance.message,
            "timestamp": instance.timestamp.isoformat()
        }

# serializers.py (continued)

class ChatOverviewSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    is_sender = serializers.BooleanField(read_only=True)
    chat_partner = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)



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
            image_file = q.get('image', None)
            choices = [Choice(**c) for c in q['choices']]

            # Create the Question object first (so it has an ImageField instance)
            question = Question(text=q['text'], choices=choices)

            if isinstance(image_file, InMemoryUploadedFile):
                # Make sure to use .put() on the actual image field
                question.image.put(
                    image_file,
                    content_type=image_file.content_type,
                    filename=image_file.name
                )

            questions.append(question)

        quiz = Quiz(title=validated_data['title'],
                    description=validated_data.get('description', ''),
                    questions=questions)
        quiz.save()
        return quiz


    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        questions_data = validated_data.get('questions')
        if questions_data:
            updated_questions = []

            for idx, q in enumerate(questions_data):
                choices = [Choice(**c) for c in q['choices']]
                question = Question(text=q['text'], choices=choices)

                image_file = q.get('image', None)
                if isinstance(image_file, InMemoryUploadedFile):
                    question.image.put(
                        image_file,
                        content_type=image_file.content_type,
                        filename=image_file.name
                    )
                elif idx < len(instance.questions) and instance.questions[idx].image:
                    # Reuse old image if not replaced
                    question.image = instance.questions[idx].image

                updated_questions.append(question)

            instance.questions = updated_questions

        instance.save()
        return instance
    
    def to_representation(self, instance):
        data = {
            'id': str(instance.id),
            'title': instance.title,
            'description': instance.description,
            'created_at': instance.created_at,
            'questions': []
        }

        for i, q in enumerate(instance.questions):
            q_data = {
                'text': q.text,
                'image': f'/api/quizzes/{str(instance.id)}/questions/{i}/image/' if q.image else None,
                'choices': [{'text': c.text, 'is_correct': c.is_correct} for c in q.choices]
            }
            data['questions'].append(q_data)

        return data

    
class FavoriteSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField()
    article_id = serializers.CharField() 

    def create(self, validated_data):
        artikel_id = validated_data['article_id']
        artikel = Artikel.objects.get(id=artikel_id)
        return Favorite.objects.create(
            user_id=validated_data['user_id'],
            article_id=artikel
        )

    def update(self, instance, validated_data):
        instance.user_id = validated_data.get('user_id', instance.user_id)
        
        artikel_id = validated_data.get('article_id')
        if artikel_id:
            artikel = Artikel.objects.get(id=artikel_id)
            instance.article_id = artikel

        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "user_id": instance.user_id,
            "article_id": str(instance.article_id.id),  
        }

class SummarySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    original_text = serializers.CharField()
    summarized_text = serializers.CharField(required=False)  
    article_id = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        text = validated_data['original_text']
        article_id = validated_data['article_id']
        article = Artikel.objects.get(id=article_id)

        summary_text = validated_data.get('summarized_text') or summarize_text(text)

        summary_instance = Summary(
            original_text=text,
            summarized_text=summary_text,
            article_id=article
        )
        summary_instance.save()
        return summary_instance

    def update(self, instance, validated_data):
        instance.original_text = validated_data.get('original_text', instance.original_text)

        if 'summarized_text' in validated_data:
            instance.summarized_text = validated_data['summarized_text']
        elif 'original_text' in validated_data:
            instance.summarized_text = summarize_text(instance.original_text)

        if 'article_id' in validated_data:
            instance.article_id = Artikel.objects.get(id=validated_data['article_id'])

        instance.updated_at = datetime.utcnow()
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "original_text": instance.original_text,
            "summarized_text": instance.summarized_text,
            "article_id": str(instance.article_id.id) if instance.article_id else None,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
