from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderServiceError

endereco = "SEU ENDEREÇO, SUA CIDADE, SC, Brasil"

locator = Nominatim(
    user_agent="meu_agente_v1"
)

try:
    print(f"Buscando endereço: {endereco}")

    local = locator.geocode(endereco)

    if local:
        print(f"Endereço Formatado: {local.address}")
        print(f"Latitude = {local.latitude}")
        print(f"Longitude = {local.longitude}")
    else:
        print("Erro: Nenhum resultado encontrado para este endereço.")

except GeocoderUnavailable:
    print("Erro: O serviço de geocodificação está indisponível.")

except GeocoderServiceError as e:
    print(f"Erro no serviço: {e}")

except Exception as e:
    print(f"Erro inesperado: {e}")