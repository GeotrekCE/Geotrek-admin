# -*- coding: utf-8 -*-

import factory

from caminae.core.factories import (
    TopologyFactory,
    TopologyInBoundsRandomGeomFactory,
    TopologyInBoundsExistingGeomFactory,
)

from . import models


class InfrastructureTypeFactory(factory.Factory):
    FACTORY_FOR = models.InfrastructureType

    label = factory.Sequence(lambda n: u"Type %s" % n)
    type = models.INFRASTRUCTURE_TYPES.BUILDING


## Infrastructure ##

class InfrastructureFactory(TopologyFactory):
    FACTORY_FOR = models.Infrastructure
    name = factory.Sequence(lambda n: u"Infrastructure %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory)


class InfrastructureInBoundsRandomGeomFactory(InfrastructureFactory):
    @classmethod
    def create_pathaggregation_from_topo(cls, topo_mixin):
        return TopologyInBoundsRandomGeomFactory.create_pathaggregation_from_topo(topo_mixin)


class InfrastructureInBoundsExistingGeomFactory(InfrastructureFactory):
    @classmethod
    def create_pathaggregation_from_topo(cls, topo_mixin):
        return TopologyInBoundsExistingGeomFactory.create_pathaggregation_from_topo(topo_mixin)


## Signage ##

class SignageFactory(TopologyFactory):
    FACTORY_FOR = models.Signage

    name = factory.Sequence(lambda n: u"Signage %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory, type=models.INFRASTRUCTURE_TYPES.SIGNAGE)


class SignageInBoundsExistingGeomFactory(SignageFactory):
    @classmethod
    def create_pathaggregation_from_topo(cls, topo_mixin):
        return TopologyInBoundsExistingGeomFactory.create_pathaggregation_from_topo(topo_mixin)


class SignageInBoundsRandomGeomFactory(SignageFactory):
    @classmethod
    def create_pathaggregation_from_topo(cls, topo_mixin):
        return TopologyInBoundsRandomGeomFactory.create_pathaggregation_from_topo(topo_mixin)

