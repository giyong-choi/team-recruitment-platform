from django.shortcuts import render
from django.views import View

class MainView(View):
    def get(self, request):
        return render(request, 'main.html')

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')
