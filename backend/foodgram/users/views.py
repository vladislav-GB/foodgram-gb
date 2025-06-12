from rest_framework import permissions, status, views
from rest_framework.response import Response
from .serializers import UserAvatarSerializer


class UserAvatarView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserAvatarSerializer

    def get(self, request):
        serializer = UserAvatarSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserAvatarSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = UserAvatarSerializer(
            request.user, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
