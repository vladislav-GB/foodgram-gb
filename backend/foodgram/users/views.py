from rest_framework import permissions, status, views
from rest_framework.response import Response
from .serializers import UserAvatarSerializer

class UserAvatarView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserAvatarSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserAvatarSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
