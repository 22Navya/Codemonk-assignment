from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from .models import User, Paragraph, WordIndex
from .serializers import UserSerializer, ParagraphSerializer
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.db.models import Count

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)

class ParagraphViewSet(viewsets.ModelViewSet):
    queryset = Paragraph.objects.all()
    serializer_class = ParagraphSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        text = request.data.get('text', '')
        paragraphs = text.split('\n\n')
        for paragraph in paragraphs:
            paragraph_instance = Paragraph.objects.create(text=paragraph)
            words = paragraph.lower().split()
            unique_words = set(words)
            for word in unique_words:
                WordIndex.objects.create(word=word, paragraph=paragraph_instance)
        return Response({'status': 'Paragraphs indexed'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def search(self, request):
        word = request.query_params.get('word', '').lower()
        paragraphs = Paragraph.objects.filter(words__word=word).annotate(word_count=Count('words')).order_by('-word_count')[:10]
        serializer = self.get_serializer(paragraphs, many=True)
        return Response(serializer.data)

