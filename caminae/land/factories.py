# -*- coding: utf-8 -*-

import factory

from caminae.core.factories import TopologyMixinFactory
from caminae.common.factories import OrganismFactory
from . import models


class WorkManagementEdgeFactory(factory.Factory):
    FACTORY_FOR = models.WorkManagementEdge

    topo_object = factory.SubFactory(TopologyMixinFactory)
    organization = factory.SubFactory(OrganismFactory())
