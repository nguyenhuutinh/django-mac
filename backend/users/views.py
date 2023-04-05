from django.shortcuts import render
from rest_framework.exceptions import ParseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions, mixins
from users.serializer import RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
import re

from users.models import User  # noqa
import pytesseract
from PIL import Image
import cv2


# Create your views here.
class AuthView(APIView):
    """
    """

    def get(self, request, format=None):
        return Response({'detail': "GET Response"})

    def post(self, request, format=None):
        try:
            data = request.DATA
        except ParseError as error:
            return Response(
                'Invalid JSON - {0}'.format(error.detail),
                status=status.HTTP_400_BAD_REQUEST
            )
        if "user" not in data or "password" not in data:
            return Response(
                'Wrong credentials',
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = User.objects.first()
        if not user:
            return Response(
                'No default user, please create one',
                status=status.HTTP_404_NOT_FOUND
            )

        token = Token.objects.get_or_create(user=user)

        return Response({'detail': 'POST answer', 'token': token[0].key})


class RegisterApi(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RegisterSerializer
    def post(self, request, *args,  **kwargs):
        print("haha")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User Created Successfully.  Now perform Login to get your token",
        })
    def get(self, request, *args,  **kwargs):
        print("haha")

        # Open the image file
        # img = Image.open('/Users/nguyenhuutinh/Projects/MyProjects/GitHub/django-mac/backend/data/test2.jpg')

        # # Use pytesseract to convert the image to text
        # text = pytesseract.image_to_string(img)
        # pattern = r'\b(1[0-9]{3,}|[2-9][0-9]{3,})\.\d*%|\b(1[0-9]{3,}|[2-9][0-9]{3,})%'

        # # Use the regex search function to find any percentage value greater than or equal to 1000 in the text
        # match = re.search(pattern, text)

        # # If a percentage value greater than or equal to 1000 is found, print it
        # if match:
        #     print(f"Percentage value greater than or equal to 1000 found: {match.group(0)}")


        # # Load the image file
        # img = cv2.imread('/Users/nguyenhuutinh/Projects/MyProjects/GitHub/django-mac/backend/data/test-2.jpg')

        # # Load the pre-trained neural network model for nudity detection
        # model = cv2.dnn.readNetFromCaffe('/Users/nguyenhuutinh/Projects/MyProjects/GitHub/django-mac/backend/data/deploy.prototxt', '/Users/nguyenhuutinh/Projects/MyProjects/GitHub/django-mac/backend/data/res10_300x300_ssd_iter_140000.caffemodel')

        # # Define the classes for the neural network model
        # classes = ['background', 'person']
        # if img is None or img.shape[0] == 0 or img.shape[1] == 0:
        #     raise ValueError('Invalid input image')
        # # Convert the image to a blob
        # input_size = (300, 300)

        # blob = cv2.dnn.blobFromImage(img, 1.0, input_size, (104.0, 177.0, 123.0))

        # # Set the input for the neural network model
        # model.setInput(blob)

        # # Perform forward pass to get the output from the neural network model
        # output = model.forward()

        # # Check if any of the detected objects are classified as a person
        # for i in range(output.shape[2]):
        #     confidence = output[0, 0, i, 2]
        #     if confidence > 0.5 and classes[int(output[0, 0, i, 1])] == 'person':
        #         print('Nudity detected')
        #         break
        return Response({"hello":"text"})
