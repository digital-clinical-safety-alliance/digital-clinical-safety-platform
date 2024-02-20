# Generated by Django 4.2.6 on 2024-02-20 16:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0003_alter_project_options_alter_userprofile_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="access",
            field=models.CharField(
                choices=[("PR", "private"), ("ME", "members"), ("PU", "public")],
                default="PU",
                max_length=10,
                verbose_name="View access",
            ),
        ),
    ]
