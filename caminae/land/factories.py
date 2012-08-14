# -*- coding: utf-8 -*-

import factory

from caminae.core.factories import TopologyMixinFactory
from caminae.common.factories import OrganismFactory
from . import models


class WorkManagementEdgeFactory(TopologyMixinFactory):
    FACTORY_FOR = models.WorkManagementEdge

    organization = factory.SubFactory(OrganismFactory)
