from mongoengine import Document, StringField, DateTimeField, FileField, ListField, EmbeddedDocument, fields, ReferenceField
from datetime import datetime
from django.db import models

class Artikel(Document):
    title = StringField(required=True)
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    image = FileField(required=False, null=True)  # Optional image
    author = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'article'}
class ChatMessage(Document):
    sender = StringField(required=True)  
    receiver = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'chat'}

class Choice(EmbeddedDocument):
    text = fields.StringField(required=True)
    is_correct = fields.BooleanField(default=False)


class Question(EmbeddedDocument):
    text = fields.StringField(required=True)
    image = fields.ImageField(required=False)  # Optional image
    choices = fields.EmbeddedDocumentListField(Choice, required=True)


class Quiz(Document):
    title = fields.StringField(required=True)
    description = fields.StringField()
    questions = fields.EmbeddedDocumentListField(Question)
    created_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'quiz'}

class Favorite(Document):
    user_id = fields.StringField(required=True)  # could be user ID or username
    article_id = fields.ReferenceField('Artikel', required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)

class Summary(Document):
    original_text = StringField(required=True)
    summarized_text = StringField()
    article_id = ReferenceField('Artikel', required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
