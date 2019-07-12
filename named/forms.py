# _*_ coding: utf-8 _*_

from django.forms import ModelForm
from  named.models import  TDnsRecords as dns_record
from  named.models import  TDnsXfrTable as dns_xfr


class dns_recordForm(ModelForm):
    class Meta:
        model = dns_record
        fields = ['data','host','type','zone','ttl']

class dns_xfrForm(ModelForm):
    class Meta:
        model = dns_xfr
        fields = ['zone','client']


