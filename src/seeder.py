from tests.factories.RelationFactory import RelationFactory

n = 100
for i in range(n):
    RelationFactory().create()
