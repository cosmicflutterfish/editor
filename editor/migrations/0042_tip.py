# Generated by Django 2.1.15 on 2020-04-06 15:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0041_auto_20191030_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('text', models.TextField()),
                ('link', models.URLField(blank=True, null=True, verbose_name='Link to more information')),
                ('link_text', models.CharField(blank=True, max_length=200, null=True)),
                ('editoritem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='used_in_tips', to='editor.EditorItem', verbose_name='A question or exam demonstrating the tip')),
            ],
        ),
    ]
