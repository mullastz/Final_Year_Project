from rest_framework import serializers
from .models import BlockchainTransactionLog

class BlockchainTransactionLogSerializer(serializers.ModelSerializer):
    performed_by = serializers.SerializerMethodField()

    class Meta:
        model = BlockchainTransactionLog
        fields = [
            "tx_hash",
            "timestamp",
            "system_id",
            "table_id",
            "function_called",
            "action_type",
            "gas_used",
            "block_number",
            "status",
            "performed_by"
        ]

    def get_performed_by(self, obj):
        return obj.performed_by.email if obj.performed_by else None

