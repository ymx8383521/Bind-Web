# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
import django.utils.timezone as timezone


class TDnsRecords(models.Model):
    id = models.BigAutoField(primary_key=True)
    zone = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    data = models.CharField(max_length=255)
    ttl = models.IntegerField(blank=True, null=True)
    mx_priority = models.IntegerField(blank=True, null=True)
    refresh = models.IntegerField(blank=True,null=True)
    retry = models.IntegerField(blank=True,null=True)
    expire = models.IntegerField(blank=True,null=True)
    minimum = models.IntegerField(blank=True,null=True)
    serial = models.BigIntegerField(blank=True,null=True)
    resp_person = models.CharField(max_length=64,blank=True,null=True)
    primary_ns = models.CharField(max_length=64, blank=True, null=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 't_dns_records'


class TDnsXfrTable(models.Model):
    id = models.BigAutoField(primary_key=True)
    zone = models.CharField(max_length=255)
    client = models.CharField(max_length=255)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 't_dns_xfr_table'
