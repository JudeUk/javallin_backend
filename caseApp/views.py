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


uri = "mongodb+srv://javallin:<javallin>@javallinmongodb.par0ddp.mongodb.net/?retryWrites=true&w=majority&appName=JavallinMongoDb"

huggingFaceToken = "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"
huggingFaceWriteToken = "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"

client = pymongo.MongoClient("mongodb+srv://javallin:javallin@javallinmongodb.par0ddp.mongodb.net/?retryWrites=true&w=majority&appName=JavallinMongoDb"
)
db = client.sample_mflix
collection =db.movies




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@permission_classes([AllowAny])
def upload_file_(request):
    if request.method == 'POST' and request.FILES:
        # uploaded_file = request.FILES['factsOfCase']
        uploaded_files = request.FILES.getlist('facts of case')

        for f in request.FILES.getlist('facts of case'):
             print(f)

        # print(uploaded_file)
        # file_instance = UploadedFile(file=uploaded_file)
        # file_instance.save()
        extracted_texts = []  # Store text string for each file

        for f in uploaded_files:
                file_extension = f.name.split('.')[-1].lower()
                try:
                        file_content = f.read()
                        print(f.content_type)
                        # with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                        #         temp_file.write(f.read())
                                # temp_file.flush()
                        # if file_extension == 'pdf':
                        #     # with open(f, 'rb') as pdf_file:
                        #         pdf_reader = PyPDF2.PdfReader(temp_file)
                        #         # pdf_reader = PyPDF2.PdfReader(pdf_file)
                        #         text = '\n'.join([page.extract_text() for page in pdf_reader.pages])
                        #         extracted_texts.append(text)
                        # elif file_extension == 'docx':
                        #     text = docx2txt.process(temp_file)
                        #     extracted_texts.append(text)
                        # else:
                        #     raise ValueError("Unsupported file type: {}".format(file_extension))
                except Exception as e:
                    return JsonResponse({'error': 'Error extracting text from file: {}'.format(e)}, status=422)

        return JsonResponse({'message': 'Text extracted successfully', 'texts': extracted_texts}, status=200)

    return JsonResponse({'error': 'No file provided'}, status=400)


        
@csrf_exempt
@permission_classes([AllowAny])
def upload_file(request):
    if request.method == 'POST' and request.FILES:
        uploaded_files = request.FILES.getlist('facts of case')

        extracted_texts = []

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
                else:
                    raise ValueError("Unsupported file type: {}".format(file_extension))
            except Exception as e:
                return JsonResponse({'error': 'Error extracting text from file: {}'.format(e)}, status=422)

        return JsonResponse({'message': 'Text extracted successfully', 'texts': extracted_texts}, status=200)

    return JsonResponse({'error': 'No file provided'}, status=400)






class CaseViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = CaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



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
        
        
    #    query_ve =  generate_embeddigns(serializer)
        results =  collection.aggregate([
            
            {
                "$vectorSearch":{
                        "queryVector":generate_embeddings('Space Movies'),
                        "path":"plot_embeddings",
                        "numCandidates":100,
                        "limit":4,
                        "index":"PlotSemanticSearch",
                }}
        ]);

        for doc in results:
            print({doc["title"]})



        if serializer.is_valid():
           
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    



API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": f"Bearer {huggingFaceToken}"}


def generate_embeddings(text: str) -> list[float]:
	
	response = requests.post(API_URL, headers={"Authorization": f"Bearer {huggingFaceWriteToken}"}, json={"inputs":text})
	return response.json()




# used to generate the vector embeddings and store in the db
# loop to generate embeddings for each record in Db
# for doc in collection.find({'plot':{"$exists":True}}).limit(50):
# 	doc['plot_embeddings']= generate_embeddings(doc['plot'])
# 	collection.replace_one({'_id':doc['_id']},doc)
# 	print('done check db collections now')

# query = "Sexy movies"

# results =  collection.aggregate([
       
#        {
#           "$vectorSearch":{
#                  "queryVector":generate_embeddings(query),
#                  "path":"plot_embeddings",
#                  "numCandidates":100,
#                  "limit":4,
#                  "index":"PlotSemanticSearch",
#           }}
# ]);

# for doc in results:
#        print({doc["title"]})