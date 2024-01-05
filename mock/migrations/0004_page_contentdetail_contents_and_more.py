# Generated by Django 5.0 on 2023-12-29 02:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('mock', '0003_content_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('mock.product',),
        ),
        migrations.AddField(
            model_name='contentdetail',
            name='contents',
            field=models.ManyToManyField(to='mock.content'),
        ),
        migrations.AlterField(
            model_name='contentdetail',
            name='detail_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'app_label': 'mock'}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.DeleteModel(
            name='ContentStyle',
        ),
    ]