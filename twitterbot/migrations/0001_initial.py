# Generated by Django 3.1 on 2022-09-09 12:06

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('tweet_id', models.CharField(max_length=100, unique=True)),
                ('text', models.CharField(blank=True, max_length=1000, null=True)),
                ('image', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default=' ', max_length=500), blank=True, null=True, size=None)),
                ('tweeted', models.BooleanField(default=False)),
                ('tweet_meta', models.JSONField(blank=True, default=dict, null=True)),
                ('video', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default=' ', max_length=500), blank=True, null=True, size=None)),
                ('likes', models.CharField(blank=True, max_length=50, null=True)),
                ('retweet', models.CharField(blank=True, max_length=50, null=True)),
                ('screen_name', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TwitterAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('TESTING', 'TESTING'), ('INACTIVE', 'INACTIVE'), ('BANNED', 'BANNED'), ('SUSPENDED', 'SUSPENDED')], default='ACTIVE', max_length=100)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('screen_name', models.CharField(blank=True, max_length=15, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('password', models.CharField(blank=True, max_length=40, null=True)),
                ('country', models.CharField(blank=True, max_length=40, null=True)),
                ('access_key', models.CharField(blank=True, max_length=100, null=True)),
                ('access_secret', models.CharField(blank=True, max_length=100, null=True)),
                ('consumer_key', models.CharField(blank=True, max_length=100, null=True)),
                ('consumer_secret', models.CharField(blank=True, max_length=100, null=True)),
                ('account_type', models.CharField(blank=True, choices=[('ART', 'ART'), ('XANALIA_NFT', 'XANALIA_NFT'), ('MKT_MEDIA', 'MKT_MEDIA')], max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TwitterUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('screen_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TwitterJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('job_type', models.CharField(choices=[('TWEET_TEXT', 'TWEET_TEXT'), ('TWEET_IMAGE', 'TWEET_IMAGE'), ('TWEET', 'TWEET'), ('LIKE', 'LIKE'), ('RETWEET', 'RETWEET'), ('FOLLOW_SINGLE_USER', 'FOLLOW_SINGLE_USER'), ('UNFOLLOW', 'UNFOLLOW'), ('UPDATE_ART_PROFILE', 'UPDATE_ART_PROFILE'), ('MULTIPLE_FOLLOW', 'MULTIPLE_FOLLOW')], max_length=100)),
                ('status', models.CharField(blank=True, choices=[('P', 'PENDING'), ('C', 'COMPLETED'), ('F', 'FAILED'), ('I', 'In-progress'), ('CN', 'CANCELED')], max_length=2, null=True)),
                ('tweet_id', models.CharField(blank=True, max_length=255, null=True)),
                ('image_path', models.CharField(blank=True, max_length=255, null=True)),
                ('text_message', models.CharField(blank=True, max_length=255, null=True)),
                ('follow_user', models.CharField(blank=True, max_length=100, null=True)),
                ('last_error', models.TextField(blank=True, null=True)),
                ('target_username', models.ManyToManyField(related_name='target_insta_users', to='twitterbot.TwitterUser')),
                ('twitter_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='twitterbot.twitteraccount')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TwitterGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('desc', models.CharField(blank=True, max_length=200, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TwitterActionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('action_type', models.CharField(blank=True, choices=[('LIKE', 'LIKE'), ('TWEET', 'TWEET'), ('FOLLOW', 'FOLLOW'), ('UNFOLLOW', 'UNFOLLOW'), ('TWEET_TEXT', 'TWEET_TEXT'), ('TWEET_IMAGE', 'TWEET_IMAGE'), ('RETWEET', 'RETWEET'), ('COMMENT', 'COMMENT'), ('MEDIA_POST', 'MEDIA_POST')], max_length=32, null=True)),
                ('target_id', models.CharField(blank=True, max_length=100, null=True)),
                ('target_screen_name', models.CharField(blank=True, max_length=100, null=True)),
                ('api_response', models.JSONField(blank=True, default=dict, null=True)),
                ('twitter_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='twitterbot.twitteraccount')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompetitorUserDetials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('target_user', models.CharField(blank=True, max_length=255, null=True)),
                ('followers', models.ManyToManyField(related_name='followers', to='twitterbot.TwitterUser')),
                ('following', models.ManyToManyField(related_name='following', to='twitterbot.TwitterUser')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]