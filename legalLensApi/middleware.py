# from django.http import HttpResponseMiddleware

# class AllowAllOriginsMiddleware(HttpResponseMiddleware):

#     def __init__(self, get_response):
#         super().__init__(get_response)

#     def process_response(self, request, response):
#         response["Access-Control-Allow-Origin"] = "*"
#         return response