.. _fixture-import:

======================
Fixtures
======================

Import during initial installation
-----------------------------------

.. important::

  - Each of these commands can be run individually. They are part of the global ``load_data.sh`` script.
  - The ``load_data.sh`` script is intended only for the initial setup. Do not run it again after the first installation, especially in a production environment, as it will overwrite any manually entered or modified data (e.g., paths, infrastructure, zoning, practices, etc.).
  - Refer to :ref:`this section <loading-fixtures>` for instructions on how to use the global ``load_data.sh`` command.

Authent imports
~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-authent-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/authent/fixtures/basic.json
                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/authent/fixtures/minimal.json

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/authent/fixtures/basic.json
                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/authent/fixtures/minimal.json

Cirkwi imports
~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-cirkwi-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/cirkwi/fixtures/cirkwi.json

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/cirkwi/fixtures/cirkwi.json

Common imports
~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-common-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/common/fixtures/basic.json
                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/common/fixtures/licenses.json
                cp -r /opt/geotrek-admin/lib/python*/site-packages/geotrek/common/fixtures/upload/ /opt/geotrek-admin/var/media/upload/

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/common/fixtures/basic.json
                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/common/fixtures/licenses.json

Core imports
~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-core-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/core/fixtures/basic.json

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/core/fixtures/basic.json

Feedback imports
~~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-feedback-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/feedback/fixtures/basic.json
                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/feedback/fixtures/management_workflow.json

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/feedback/fixtures/basic.json
                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/feedback/fixtures/management_workflow.json

Infrastructure imports
~~~~~~~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-infrastructure-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/infrastructure/fixtures/basic.json
                cp -r /opt/geotrek-admin/lib/python*/site-packages/geotrek/infrastructure/fixtures/upload/ /opt/geotrek-admin/var/media/upload/


    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/infrastructure/fixtures/basic.json

.. _fixture-land:

Land imports
~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-circulation-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/land/fixtures/circulations.json
                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/land/fixtures/basic.json

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/land/fixtures/circulations.json
                docker-compose run --rm web ./manage.py loaddata geotrek/land/fixtures/basic.json

Maintenance imports
~~~~~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-maintenance-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/maintenance/fixtures/basic.json

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/maintenance/fixtures/basic.json

Signage imports
~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-signage-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/signage/fixtures/basic.json

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/signage/fixtures/basic.json

Tourism imports
~~~~~~~~~~~~~~~~
.. md-tab-set::
    :name: loaddata-tourism-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/tourism/fixtures/basic.json
                cp -r /opt/geotrek-admin/lib/python*/site-packages/geotrek/tourism/fixtures/upload/ /opt/geotrek-admin/var/media/upload/

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/tourism/fixtures/basic.json

Trekking imports
~~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-trekking-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/trekking/fixtures/basic.json
                cp -r /opt/geotrek-admin/lib/python*/site-packages/geotrek/trekking/fixtures/upload/ /opt/geotrek-admin/var/media/upload/

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/trekking/fixtures/basic.json

Zoning imports
~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-zoning-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/zoning/fixtures/basic.json

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/zoning/fixtures/basic.json

Import after initial installation
----------------------------------

.. important::

  These commands can be run once the Outdoor or Sensitivity modules are enabled.

.. _fixture-outdoor:

Outdoor imports
~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-outdoor-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/outdoor/fixtures/basic.json

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/outdoor/fixtures/basic.json

.. seealso::
  To enable Outdoor module, refer to :ref:`this section <outdoor>`.

.. _fixture-sensitivity:

Sensitivity imports
~~~~~~~~~~~~~~~~~~~~

.. md-tab-set::
    :name: loaddata-sensitivity-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/sensitivity/fixtures/basic.json
                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/sensitivity/fixtures/rules.json
                cp -r /opt/geotrek-admin/lib/python*/site-packages/geotrek/sensitivity/fixtures/upload/rules/ /opt/geotrek-admin/var/media/upload/

    .. md-tab-item:: With Docker

         .. code-block:: python

                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/geotrek/sensitivity/fixtures/basic.json
                docker compose run --rm web ./manage.py loaddata rules

.. seealso::
  To enable Sensitivity module, refer to :ref:`this section <sensitivity>`.