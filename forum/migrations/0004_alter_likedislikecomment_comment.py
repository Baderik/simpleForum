# Generated by Django 4.0.4 on 2022-11-16 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_alter_likedislikearticle_article_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='likedislikecomment',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.comment'),
        ),
    ]
