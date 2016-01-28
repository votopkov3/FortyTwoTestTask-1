# -*- coding: utf-8 -*-
from south.v2 import SchemaMigration
from django.core.management import call_command


class Migration(SchemaMigration):

    def forwards(self, orm):
        call_command("loaddata", "initial_data.json")


    def backwards(self, orm):
        pass


complete_apps = ['hello']
