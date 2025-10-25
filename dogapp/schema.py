# dogapp/schema.py

import graphene
from graphene_django.types import DjangoObjectType
from dogapp.models import Dog
from dogapp.permissions import IsOwnerGQL  # 👈 Import the centralized GraphQL permission
from graphql import GraphQLError
import graphql_jwt


class DogType(DjangoObjectType):
    class Meta:
        model = Dog


class Query(graphene.ObjectType):
    dog = graphene.Field(DogType, id=graphene.Int())

    def resolve_dog(self, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required.")
        try:
            dog = Dog.objects.get(pk=id)
            # 👇 Centralized object-level permission check
            IsOwnerGQL(user, dog)
            return dog
        except Dog.DoesNotExist:
            return None


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
