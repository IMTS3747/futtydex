# Generated for Futtydex position metadata.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("bd_models", "0019_guildconfig_tips_enabled")]

    operations = [
        migrations.AddField(
            model_name="ball",
            name="positions",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Positions this Futtydex can play. Select one or more, or leave empty for no position.",
            ),
        )
    ]
