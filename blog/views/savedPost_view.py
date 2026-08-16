from rest_framework import mixins, viewsets
from blog.models import SavedPost
from rest_framework.permissions import IsAuthenticated
from blog.serializers.savedPost_serializer import SavedPostSerializer 

class SavedPostView(mixins.ListModelMixin,mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    
    permission_classes = [IsAuthenticated]
    serializer_class = SavedPostSerializer
    
    def get_queryset(self):
        user = self.request.user
        return SavedPost.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)