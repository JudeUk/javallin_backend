from io import BytesIO
import tempfile
import PyPDF2
import docx2txt
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Case
from .serializers import CaseDataSerializer, CaseSerializer
from django import views
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, action
import pymongo
import requests
import numpy as np


uri = "mongodb+srv://javallin:<javallin>@javallinmongodb.par0ddp.mongodb.net/?retryWrites=true&w=majority&appName=JavallinMongoDb"

huggingFaceToken = "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"
huggingFaceWriteToken = "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"

API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": f"Bearer {huggingFaceToken}"}

client = pymongo.MongoClient("mongodb+srv://javallin:javallin@javallinmongodb.par0ddp.mongodb.net/?retryWrites=true&w=majority&appName=JavallinMongoDb"
)
db = client.sample_mflix
collection =db.movies
collectionCases = db.cases




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  




@api_view(['POST'])
@permission_classes([AllowAny])
def create(request):
        case = Case.objects.create(
            request.data.get('facts') ,
            request.data.get('facts') ,
            request.data.get('facts')            
        )
        serializer = CaseDataSerializer(data=request.data)

        print(serializer)




class CaseViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = CaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)




# Function to generate embeddings for text
def generate_embeddings(text: str) -> list[float]:
    response = requests.post(API_URL, headers={"Authorization": f"Bearer {huggingFaceWriteToken}"}, json={"inputs": text})
    # embeddings = response.json()["outputs"][0]["embeddings"]
    return response.json()

# Function to compute the average embedding
def compute_average_embedding(embeddings):
    # Convert list of embeddings to numpy array
    embeddings_array = np.array(embeddings)
    # Compute mean along the first axis (axis=0) to get average embedding
    average_embedding = np.mean(embeddings_array, axis=0)
    return average_embedding.tolist()

# Modify the upload_file function
@csrf_exempt
@permission_classes([AllowAny])
def upload_file(request):
    if request.method == 'POST' and request.FILES:
        uploaded_files = request.FILES.getlist('facts of case')

        extracted_texts = []
        embeddings = []
        case_numbers = []

        for f in uploaded_files:
            file_extension = f.name.split('.')[-1].lower()

            try:
                print(f.content_type)
                if file_extension in ['pdf', 'docx']:
                    # In-memory file handling
                    file_content = f.read()
                    in_memory_file = BytesIO(file_content)

                    if file_extension == 'pdf':
                        pdf_reader = PyPDF2.PdfReader(in_memory_file)
                        text = '\n'.join([page.extract_text() for page in pdf_reader.pages])
                        extracted_texts.append(text)
                    elif file_extension == 'docx':
                        text = docx2txt.process(in_memory_file)
                        extracted_texts.append(text)
                    print(extracted_texts)    

                    
                    # Generate embeddings for the extracted text
                    embedding = generate_embeddings(extracted_texts)
                    print(embedding)
                    embeddings.append(embedding)
                    
                else:
                    raise ValueError("Unsupported file type: {}".format(file_extension))
            except Exception as e:
                return JsonResponse({'error': 'Error extracting text from file: {}'.format(e)}, status=422)

        # Compute average embedding for each document
        average_embeddings = [compute_average_embedding(doc_embeddings) for doc_embeddings in embeddings]

        # Compare the uploaded document with documents in your database
        for average_embedding in average_embeddings:
            # You need to replace 'Space Movies' with the text you want to compare with
            # results =  collection.aggregate([
            #     {
            #         "$vectorSearch": {
            #             "queryVector": average_embedding,
            #             "path": "plot_embeddings",
            #             "numCandidates": 100,
            #             "limit": 4,
            #             "index": "PlotSemanticSearch",
            #         }
            #     }
            # ])

            resultsCases =  collectionCases.aggregate([
                {
                    "$vectorSearch": {
                        "queryVector": average_embedding,
                        "path": "average_embedding",
                        "numCandidates": 100,
                        "limit": 4,
                        "index": "caseSemanticSearch",
                    }
                }
            ])


            for doc in resultsCases:
                # print(doc["title"]
                case_numbers.append(doc["case_number"])

                print(doc["case_number"])

        return JsonResponse({'message': 'Text extracted successfully', 'texts': extracted_texts, 'case_numbers':len(case_numbers)}, status=200)

    return JsonResponse({'error': 'No file provided'}, status=400)
