import graphene


class FetchWorkerDataGQLType(graphene.ObjectType):
    idpn = graphene.ID()
    first_name = graphene.String()
    last_name = graphene.String()
