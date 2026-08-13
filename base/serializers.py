from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):

    class Meta:
        abstract = True
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )

    def create(self, validated_data):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
            validated_data["updated_by"] = request.user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            validated_data["updated_by"] = request.user

        return super().update(instance, validated_data)