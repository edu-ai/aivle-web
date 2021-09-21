from dj_rest_auth.models import TokenModel
from dj_rest_auth.serializers import TokenSerializer


class CustomTokenSerializer(TokenSerializer):
    """
        Serializer for Token model.
        """

    class Meta:
        model = TokenModel
        fields = ('user', 'key')
