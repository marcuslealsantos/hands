import json
from urllib.request import urlopen

from django.contrib import messages
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http.response import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from openpyxl.workbook.workbook import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from .models import PointOfSale, StateProvince, Visit


def index(request):
    place = "McDonald's"
    state = StateProvince.objects.get(code="MG")
    
    # 1. Filtragem por precisão e duração. 
    # Eliminar registros com precisão maior que 100m e duração maior que 90min.
    visits = Visit.objects.filter(
        precision__lt=100, total_time_in_min__lt=90, 
        place__name=place, place__address__city__state__code=state) 

    count_visits_total = visits.count()
    count_users_total = visits.values('user_id').annotate(
        count=Count('user_id')).count()

    infos = dict()
    series_days_of_week = [
        {'name': 'Sunday', 'values':[]}, 
        {'name': 'Monday', 'values':[]}, 
        {'name': 'Tuesday', 'values':[]}, 
        {'name': 'Wednesday', 'values':[]},
        {'name': 'Thursday', 'values':[]}, 
        {'name': 'Friday', 'values':[]}, 
        {'name': 'Saturday', 'values':[]}
    ]
    series_day_periods = [
        {'name': 'Manhã', 'values':[]}, 
        {'name': 'Almoço', 'values':[]}, 
        {'name': 'Tarde', 'values':[]}, 
        {'name': 'Noite', 'values':[]},
        {'name': 'Madrugada', 'values':[]},
    ]

    for visit in visits:
        key = "{}-{}".format(visit.place, visit.place.address.zip_code)
        
        if not infos.get(key):
            _visits=visits.filter(place=visit.place)
            item = dict(
                visit=visit

                # 2. Contagem de visitas e usuários aos PDVs.
                ,count_visits=_visits.count()
                ,count_users=_visits.values(
                    'user_id').annotate(count=Count('user_id')).count() 

                # 3. Criação de visualização dos dias da semana das visitas aos PDVs.
                ,count_days_of_week=[ 
                    {week_day[1]:_visits.filter(arrival__week_day=week_day[0]).count()}
                    for week_day in Visit.DAYS_OF_WEEK ]
                
                # 4. Criação de visualização dos períodos do dia das visitas aos PDVs. (Manhã, Almoço, Tarde, Noite)
                ,count_day_periods=[
                    {day_period[0]:_visits.filter(
                        arrival__time__range=(day_period[1], day_period[2])).count()}
                    for day_period in Visit.DAY_PERIOD]

                # 5. Criação de visualização de visitas antes e visitas depois de visitas aos PDVs
                
            )
            infos[key] = item

            # generate series to chart days of week
            if item.get('count_visits') > 100:
                for dayweek in item.get('count_days_of_week'):
                    for serie in series_days_of_week:
                        if serie['name'] in dayweek:
                            _values = list(dayweek.items())
                            serie['values'].append(_values[0][1])
                
                for dayperiod in item.get('count_day_periods'):
                    for serie in series_day_periods:
                        if serie['name'] in dayperiod:
                            _values = list(dayperiod.items())
                            serie['values'].append(_values[0][1])

    context = dict(
        infos=infos
        ,count_visits=count_visits_total
        ,count_users=count_users_total
        ,series_days_of_week=series_days_of_week
        ,series_day_periods=series_day_periods
    )
    if 'reports' in request.POST:
        wb = Workbook()
        wb.remove_sheet(wb.worksheets[0])
        sh = wb.create_sheet('vivists')

        sh.append([
            '_ID'
            ,'EUID'
            ,'ARRIVAL'
            ,'DEPARTURE'
            ,'PDV'
            ,'STREET'
            ,'POSTCODE'
            ,'SUBURB'
            ,'CITY'
            ,'VISITS'
            ,'CUSTOMERS'
            ,'COUNT_DAY_PERIODS'
            ,'COUNT_DAYS_OF_WEEK'
        ])

        for item in infos.values():
            # import pdb ; pdb.set_trace()
            visit = item.get('visit')
            sh.append([
                visit.code
                ,visit.user_id
                ,visit.arrival.strftime('%d/%m/%Y')
                ,visit.departure.strftime('%d/%m/%Y')
                ,visit.pdv
                ,visit.place.address.street or ''
                ,visit.place.address.zip_code or ''
                ,visit.place.address.suburb or ''
                ,visit.place.address.city.name
                ,item.get('count_visits')
                ,item.get('count_users')
                ,json.dumps(item.get('count_day_periods'))
                ,json.dumps(item.get('count_days_of_week'))
            ])

        response = HttpResponse(save_virtual_workbook(
            wb), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = "attachment; filename=visits.xlsx"
        return response

    return render(request, 'index.html', context)
