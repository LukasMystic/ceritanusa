from rest_framework import serializers
from .models import ChatMessage
from .models import Artikel, Quiz, Question, Choice, Favorite, Summary
from datetime import datetime

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
    summarized_text = serializers.CharField(read_only=True)
    article_id = serializers.CharField()  # <-- add this line
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        from .summarizer import summarize_text

        text = validated_data['original_text']
        summary_text = summarize_text(text)
        artikel_id = validated_data['article_id']
        artikel = Artikel.objects.get(id=artikel_id)

        summary_instance = Summary(
            original_text=text,
            summarized_text=summary_text,
            article_id=artikel
        )
        summary_instance.save()
        return summary_instance

    def update(self, instance, validated_data):
        instance.summarized_text = validated_data.get('summarized_text', instance.summarized_text)
        instance.updated_at = datetime.utcnow()

        artikel_id = validated_data.get('article_id')
        if artikel_id:
            instance.article_id = Artikel.objects.get(id=artikel_id)

        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "original_text": instance.original_text,
            "summarized_text": instance.summarized_text,
            "article_id": str(instance.article_id.id) if instance.article_id else None,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at
        }
