from django.shortcuts import render
import urllib.parse
import secrets
import requests
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
import os

def show_biodata(request):
    user_info = request.session.get('user')
    is_member = _is_member(user_info['email']) if user_info else False

    theme = read_theme()
    context = {
        'user':      user_info,
        'is_member': is_member,
        'theme':     theme,
    }
    return render(request, 'show_biodata.html', context)

def _is_member(email: str):
    """Untuk memeriksa meber yang diperbolehkan mengedit"""
    return email in settings.ALLOWED_MEMBER_EMAILS

def oauth_login(request):
    """Redirect user ke halaman login Google."""
    # CSRF protection: simpan state di session
    state = secrets.token_urlsafe(16)
    request.session['oauth_state'] = state

    params = {
        'client_id':     settings.GOOGLE_CLIENT_ID,
        'redirect_uri':  settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope':         'openid email profile',
        'state':         state,
        'access_type':   'online',
        'prompt':        'select_account',
    }

    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    return redirect(auth_url)

def oauth_callback(request):
    """Tangani callback dari Google setelah user login."""
    # 1. Validasi state (CSRF check)
    returned_state = request.GET.get('state', '')
    saved_state    = request.session.pop('oauth_state', None)

    if not saved_state or returned_state != saved_state:
        return render(request, 'show_biodata.html', {'error': 'Invalid OAuth state. Possible CSRF attack.'})

    # 2. Cek error dari Google
    error = request.GET.get('error')
    if error:
        return redirect('show_biodata')

    # 3. Tukar authorization code → access token
    code = request.GET.get('code')
    token_response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code':          code,
            'client_id':     settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri':  settings.GOOGLE_REDIRECT_URI,
            'grant_type':    'authorization_code',
        },
        timeout=10,
    )

    if token_response.status_code != 200:
        return render(request, 'show_biodata.html', {'error': 'Gagal mendapatkan token dari Google.'})

    access_token = token_response.json().get('access_token')

    # 4. Ambil info user dari Google
    userinfo_response = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10,
    )

    if userinfo_response.status_code != 200:
        return render(request, 'show_biodata.html', {'error': 'Gagal mengambil data user.'})

    user_info = userinfo_response.json()

    # 5. Simpan user info ke session (JANGAN simpan access_token di session)
    request.session['user'] = {
        'email':   user_info.get('email'),
        'name':    user_info.get('name'),
        'picture': user_info.get('picture'),
    }
    
    if 'theme' not in request.session:
        request.session['theme'] = {
            'bg_color': '#000000',
            'card_color': '#171717',
            'text_color': '#FFFFFF',
            'font': 'Poppins',
        }

    return redirect('/?toast=login_berhasil')

def oauth_logout(request):
    """Hapus session user."""
    request.session.flush()
    return redirect('/?toast=logout_berhasil')

THEME_FILE = os.path.join(os.path.dirname(__file__), 'theme.json')

DEFAULT_THEME = {
    'bg_color':   '#000000',
    'card_color': '#171717',
    'text_color': '#FFFFFF',
    'font':       'Poppins',
}

def read_theme():
    try:
        with open(THEME_FILE, 'r') as file:
            return json.load(file)
    except:
        return DEFAULT_THEME.copy()

def write_theme(theme):
    try:
        with open(THEME_FILE, 'w') as file:
            json.dump(theme, file)
    except Exception as e:
        print("Error writing theme:", e)

@require_POST
def save_theme(request):
    user_info = request.session.get('user')

    # Authorization check
    if not user_info or not _is_member(user_info['email']):
        return JsonResponse({'error': 'Error: Anda bukan anggota kelompok.'}, status=403)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    allowed_fonts = ['Poppins', 'Inter', 'Montserrat']
    font = body.get('font', 'Poppins')
    if font not in allowed_fonts:
        font = 'Poppins'

    theme = {
        'bg_color':   body.get('bg_color',   '#000000'),
        'card_color': body.get('card_color', '#171717'),
        'text_color': body.get('text_color', '#FFFFFF'),
        'accent':     body.get('accent',     '#A5CDFE'),
        'font':       font,
    }
    
    write_theme(theme)

    return JsonResponse({'status': 'ok'})