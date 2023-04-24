
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
import plotly.graph_objs as go
import json
import requests
import json
import urllib.parse

# Create your views here.
def solicitud(request):

    if request.method == "GET":
        context = request.session.get('posibles_valores')
        request.session.pop('alts', None)
        return render(request, 'components/forms/form-captura_datos_credito.html', context)

    if request.method == "POST":

        url = "http://127.0.0.1:8080/API/"  # The URL of your Django REST API endpoint
        headers = {'content-type': 'application/json'}
        
        data = {
            "command" : "calificacion-simple",
            "Monto de credito": float(request.POST.get("monto-de-credito")),
            "Tasa anual": float(request.POST.get("tasa-anual")),
            "Monto de pago": float(request.POST.get("monto-pago")),
            "Numero de pagos": int(request.POST.get("numero-pagos")),
            "Frecuencia de pago": int(request.POST.get("esquema-pagos")),
            "Ingreso mensual": float(request.POST.get("ingreso-mensual")),
            "Edad": int(request.POST.get("edad")),
            "Numero de contratos previos": int(request.POST.get("contratos-previos")),
            "Antiguedad": request.POST.get("selector-antiguedad"),
            "Ocupacion": request.POST.get("ocupacion-datalist"),
            "Empresa": request.POST.get("empresa-datalist"),
            "Estado": request.POST.get("estado-datalist"),
            "Estado civil": request.POST.get("selector-estado-civil"),
            "Genero": request.POST.get("selector-genero")
        }  # The data you want to send in the POST request

        request.session["current_data"] = data
        response = requests.post(url, headers=headers, json=data)
        #print(response.content)
        if response.status_code == 200:
            new_resource_data = response.content.decode()  # The data of the newly created resource in JSON format
            new_resource_data = json.loads(new_resource_data)
            request.session['response_data'] = new_resource_data
            
        else:
            # Oops, there was an error. Handle it here
            error_message = f"Error {response.status_code}: {response.reason}"
            return HttpResponse(json.dumps({"error": error_message}), content_type="application/json", status=response.status_code)
        
        return redirect('calificacion')
        

def calificacion(request):
    if request.method == "GET":
        context = {}
        show_button = True
        show_div = False

        response_data = request.session.get('response_data')
        etiquetas = response_data["etiquetas"]
        pesos = response_data["peso"]
        prediccion = response_data["prediccion"]

        for item in range(len(pesos)):
            pesos[item] = round(pesos[item], 4)
            datos = dict(zip(etiquetas, pesos))
            datos['Prediccion'] = round(prediccion, 4)

        datos = json.dumps(datos, ensure_ascii=False)
        context['datos'] = datos

        if(request.session.get('alts')):
            alts = request.session.get('alts')
            show_div = True
            show_button = False
            context['alts'] = request.session.get('alts', None)

        context['show_div'] = show_div
        context['show_button'] = show_button

        
        return render(request, 'components/charts/charts-waterfall.html', context)

    elif request.method == "POST":

        url = "http://127.0.0.1:8080/API/"  # The URL of your Django REST API endpoint
        headers = {'content-type': 'application/json'}
        previous_response_data = request.session.get('response_data')

        etiquetas = previous_response_data["etiquetas"]
        pesos = previous_response_data["peso"]
        prediccion = previous_response_data["prediccion"]

        for item in range(len(pesos)):
            pesos[item] = round(pesos[item], 4)
            datos = dict(zip(etiquetas, pesos))
            datos['Prediccion'] = round(prediccion, 4)

        datos = json.dumps(datos, ensure_ascii=False)

        data = request.session.get("current_data")
        tasa_por_periodo = previous_response_data["tasa por periodo"]

        data["command"] = "calificacion-alternativas"
        data["Tasa por periodo"] = tasa_por_periodo
        
        response = requests.post(url, headers=headers, json=data)

        if(response.status_code == 200):
            response_data = response.content.decode()
            response_data = json.loads(response_data)
            alts = response_data["alts"]
            request.session['alts'] = alts
            #encoded_alts = urllib.parse.quote(json.dumps(alts))
            #url=f"?alts={encoded_alts}"
            return redirect('calificacion')
        else:
            # Oops, there was an error. Handle it here
            error_message = f"Error {response.status_code}: {response.reason}"
            return HttpResponse(json.dumps({"error": error_message}), content_type="application/json", status=response.status_code)        


def alternativas(request):
    if request.method == "GET":

        response_data = request.session.get('response_data')
        etiquetas = response_data['etiquetas']
        pesos = response_data['peso']
        prediccion = response_data['prediccion']

        for item in range(len(pesos)):
            pesos[item] = round(pesos[item], 4)
            datos = dict(zip(etiquetas, pesos))
            datos['Prediccion'] = round(prediccion, 4)

        json_string = json.dumps(datos)

        alts = request.session.get("alts")
        datos = request.session.get('response_data')
        context = {'datos' : json_string, 'alts': alts}
        return render(request, 'components/charts/charts-waterfall_alternativa.html', context)          


def calificador(request):
    if request.method == 'GET':
        url = "http://127.0.0.1:8080/API/"
        response = requests.get(url)

        if response.status_code == 200:
            posibles_valores = response.json()
            genero = posibles_valores["posibles_valores"]["Genero"]
            ocupacion = posibles_valores["posibles_valores"]["Ocupacion"]
            empresa = posibles_valores["posibles_valores"]["Empresa"]
            antiguedad = posibles_valores["posibles_valores"]["Antiguedad"]
            estado = posibles_valores["posibles_valores"]["Estado"]
            estado_civil = posibles_valores["posibles_valores"]["Estado civil"]

            context = {
                'genero': genero,
                'ocupacion':ocupacion,
                'empresa':empresa,
                'antiguedad':antiguedad,
                'estado': estado,
                'estado_civil': estado_civil
            }
            request.session['posibles_valores'] = context
            return redirect('solicitud')
        else:
            error_msg = f"Error {response.status_code}: {response.reason}"
            return HttpResponse(json.dumps({"error": error_msg}), content_type="application/json", status=response.status_code)
