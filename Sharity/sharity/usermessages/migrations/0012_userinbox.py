# Generated by Django 3.2.13 on 2022-05-12 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0004_alter_profile_userlocation'),
        ('usermessages', '0011_remove_usermessage_inbox_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.ManyToManyField(related_name='inbox_content', to='usermessages.UserMessage')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to='member.profile')),
            ],
        ),
    ]
