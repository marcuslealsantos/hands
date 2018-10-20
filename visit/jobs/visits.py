import os

from django_extensions.management.jobs import BaseJob

from ..utils import load_visits


class Job(BaseJob):
    when = "daily"
    help = "Import visits"

    def execute(self):
        path = os.path.abspath(os.path.dirname(__file__))
        load_visits(path+'/Visitas.csv', point_of_sale="McDonald's", state="MG")
