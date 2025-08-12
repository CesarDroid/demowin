from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Mufa, Hilo
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable

@receiver(post_save, sender=Mufa)
def crear_hilos_mufa(sender, instance, created, **kwargs):
    print(f"🧠 Se están creando {instance.capacidad_hilos} hilos para {instance.codigo}")

    # Crear hilos si no existen aún
    if created and instance.hilos.count() == 0:
        for i in range(1, instance.capacidad_hilos + 1):
            Hilo.objects.create(
                mufa=instance,
                numero=i,
                estado='libre',
                splitter='-',
            )

    # Detectar distrito automáticamente
    if instance.latitud and instance.longitud and not instance.distrito:
        try:
            geolocator = Nominatim(user_agent="winfibra")
            location = geolocator.reverse(f"{instance.latitud}, {instance.longitud}", language='es')
            if location and 'address' in location.raw:
                distrito = location.raw['address'].get('suburb') or \
                           location.raw['address'].get('city_district') or \
                           location.raw['address'].get('town') or \
                           location.raw['address'].get('city')
                if distrito:
                    instance.distrito = distrito.upper()
                    instance.save()
                    print(f"📍 Distrito detectado: {distrito}")
        except GeocoderUnavailable:
            print("⚠️ Servicio de geolocalización no disponible.")
