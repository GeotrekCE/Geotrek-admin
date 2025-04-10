# Generated by Django 2.0.13 on 2020-04-06 14:11

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tourism", "0010_auto_20200228_2152"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER SEQUENCE t_b_contenu_touristique_categorie_id_seq RENAME TO tourism_touristiccontentcategory_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_b_contenu_touristique_type_id_seq RENAME TO tourism_touristiccontenttype_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_b_evenement_touristique_type_id_seq RENAME TO tourism_touristicenventtype_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_b_renseignement_id_seq RENAME TO tourism_informationdesk_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_b_systeme_reservation_id_seq RENAME TO tourism_reservationsystem_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_b_type_renseignement_id_seq RENAME TO tourism_informationdesktype_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_r_contenu_touristique_portal_id_seq RENAME TO tourism_touristiccontent_portal_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_r_contenu_touristique_source_id_seq RENAME TO tourism_touristiccontent_source_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_r_contenu_touristique_theme_id_seq RENAME TO tourism_touristiccontent_themes_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_r_contenu_touristique_type1_id_seq RENAME TO tourism_touristiccontent_type1_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_r_contenu_touristique_type2_id_seq RENAME TO tourism_touristiccontent_type2_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_r_evenement_touristique_portal_id_seq RENAME TO tourism_touristicevent_portal_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_r_evenement_touristique_source_id_seq RENAME TO tourism_touristicevent_source_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_r_evenement_touristique_theme_id_seq RENAME TO tourism_touristicevent_themes_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_t_contenu_touristique_id_seq RENAME TO tourism_touristiccontent_id_seq;"
        ),
        migrations.RunSQL(
            "ALTER SEQUENCE t_t_evenement_touristique_id_seq RENAME TO tourism_touristicevent_id_seq;"
        ),
    ]
