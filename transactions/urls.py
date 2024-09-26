from django.urls import path
from .views import process_transaction_file, chart_of_accounts, collections_report, bad_transactions_report, reset_system

urlpatterns = [
    path('upload/', process_transaction_file, name='upload'),
    path('chart/', chart_of_accounts, name='chart'),
    path('collections/', collections_report, name='collections'),
    path('bad_transactions/', bad_transactions_report, name='bad_transactions'),
    path('reset/', reset_system, name='reset'),
]