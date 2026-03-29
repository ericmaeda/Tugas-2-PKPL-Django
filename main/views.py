from django.shortcuts import render

def show_biodata(request):
    context = {
        'tes' : 'Cek',
    }
    
    return render(request, 'show_biodata.html', context)
