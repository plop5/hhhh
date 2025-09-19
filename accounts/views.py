from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from accounts.paises import get_ciudades_por_pais
from .models import Anuncio, FotoAnuncio
from .forms import UserCreationForm
from django.core.files.uploadedfile import InMemoryUploadedFile

def home(request):
    # Obtener los top 3 femeninos con sus fotos
    top_femeninos_raw = Anuncio.objects.filter(
        sexo__in=['mujer', 'femenino']
    ).prefetch_related('fotos').order_by('-creado')[:3]
    
    # Por ahora mostramos datos básicos sin rankings hasta hacer migraciones
    context = {
        'estadisticas': {
            'total_escorts': Anuncio.objects.count(),
            'total_ciudades': Anuncio.objects.values('ciudad').distinct().count(),
            'total_reviews': 0,
            'promedio_satisfaccion': 0
        },
        'top_femeninos': list(top_femeninos_raw),
        'top_masculinos': list(Anuncio.objects.filter(sexo__in=['hombre', 'masculino']).order_by('-creado')[:6]),
        'top_trans': list(Anuncio.objects.filter(sexo__in=['trans', 'travesti']).order_by('-creado')[:6]),
        'destacados_mes': [],
        'nuevos_verificados': list(Anuncio.objects.order_by('-creado')[:6])
    }
    return render(request, 'home.html', context)

def panel(request):
    return render(request, 'panel.html')

@login_required
def mis_anuncios(request):
    anuncios = Anuncio.objects.filter(usuario=request.user).order_by('-creado')
    return render(request, 'listado.html', {'anuncios': anuncios})

# Registro de usuario
@csrf_exempt
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('panel')
    else:
        form = UserCreationForm()
    return render(request, 'registro.html', {'form': form})

# Login de usuario
@csrf_exempt
def login_view(request):
    mensaje = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('panel')
        else:
            mensaje = 'Usuario o contraseña incorrectos.'
    return render(request, 'login.html', {'mensaje': mensaje})

# Logout de usuario
def logout_view(request):
    logout(request)
    return redirect('login')

def listado_acompanantes(request):
    anuncios = Anuncio.objects.all().order_by('-creado')
    return render(request, 'listado.html', {'anuncios': anuncios})

def listado_publico(request, categoria=None, ciudad=None):
    anuncios = Anuncio.objects.all().order_by('-creado')
    if categoria:
        anuncios = anuncios.filter(sexo=categoria)
    if ciudad:
        anuncios = anuncios.filter(ciudad__iexact=ciudad)
    return render(request, 'listado_publico.html', {'anuncios': anuncios})

@login_required
@csrf_exempt
def fotos_user(request):
    # Determinar límite por plan
    plan = getattr(request.user, 'plan', 'basico')
    max_fotos = 1 if plan == 'basico' else 10
    if request.method == 'POST':
        # Recuperar datos del anuncio desde la sesión
        anuncio_data = request.session.get('anuncio_data')
        if not anuncio_data:
            return redirect('unisex_form')
        anuncio = Anuncio.objects.create(
            usuario=request.user,
            titulo=anuncio_data.get('titulo', ''),
            descripcion=anuncio_data.get('descripcion', ''),
            ciudad=anuncio_data.get('ciudad', ''),
            pais=anuncio_data.get('pais', 'Ecuador'),
            precio=anuncio_data.get('precio', 0),
            sexo=anuncio_data.get('sexo', '')
        )
        fotos = request.FILES.getlist('fotos')
        # Enforce limit server-side
        for foto in fotos[:max_fotos]:
            FotoAnuncio.objects.create(anuncio=anuncio, imagen=foto)
        # Limpiar datos de sesión
        if 'anuncio_data' in request.session:
            del request.session['anuncio_data']
        return redirect('mis_anuncios')
    return render(request, 'onboarding/fotos_user.html', {'max_fotos': max_fotos})

@csrf_exempt
def unisex_form(request):
    ciudades = get_ciudades_por_pais("ecuador")
    if request.method == 'POST':
        # Guardar datos del formulario en sesión
        request.session['anuncio_data'] = {
            'titulo': request.POST.get('titulo', ''),
            'descripcion': request.POST.get('descripcion', ''),
            'ciudad': request.POST.get('ciudad', ''),
            'pais': request.POST.get('pais', 'Ecuador'),
            'precio': request.POST.get('precio', 0),
            'sexo': request.POST.get('sexo', ''),
        }
        return redirect('fotos_user')
    return render(request, 'onboarding/unisex_form.html', {'ciudades_ecuador': ciudades})
