from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # hash password
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField()
    sent_at = serializers.SerializerMethodField()

    # Optional: include conversation id if useful to API consumer
    # conversation = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at']
        # If you add conversation field above, include it here

    def get_sent_at(self, obj):
        return obj.sent_at.isoformat()


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages']
        read_only_fields = ['conversation_id', 'created_at', 'messages']

    def validate_participants(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('Conversation must have at least two participants.')
        return value

    def create(self, validated_data):
        participants_data = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data)
        for participant_data in participants_data:
            try:
                user_obj = User.objects.get(email=participant_data['email'])
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    f"User with email {participant_data['email']} does not exist."
                )
            conversation.participants.add(user_obj)
        return conversation
