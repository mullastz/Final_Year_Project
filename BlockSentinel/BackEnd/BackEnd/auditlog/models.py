from django.db import models
from django.conf import settings  # ✅ Use this instead of direct import from auth

class BlockchainTransactionLog(models.Model):
    tx_hash = models.CharField(max_length=100, unique=True)
    function_called = models.CharField(max_length=100)
    gas_used = models.PositiveBigIntegerField()
    status = models.CharField(max_length=10, choices=[('Success', 'Success'), ('Fail', 'Fail')])
    block_number = models.PositiveBigIntegerField()
    timestamp = models.DateTimeField()
    system_id = models.CharField(max_length=100, null=True, blank=True)
    table_id = models.CharField(max_length=100, null=True, blank=True)

    # ✅ Refer to AUTH_USER_MODEL dynamically
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.tx_hash} - {self.function_called} - {self.status}"



class BlockchainTransactionLog(models.Model):
    ACTION_CHOICES = [
        ("store", "Store Data"),
        ("update", "Update Data"),
        ("create", "Create Ledger"),
        ("delete", "Delete Entry"),
        ("read", "Read Data"),
        ("other", "Other"),
    ]

    tx_hash = models.CharField(max_length=100, unique=True)
    function_called = models.CharField(max_length=100)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default="other")
    gas_used = models.PositiveBigIntegerField()
    status = models.CharField(max_length=10)  # "Success" or "Fail"
    block_number = models.PositiveBigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    system_id = models.CharField(max_length=100, null=True, blank=True)
    table_id = models.CharField(max_length=100, null=True, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.function_called} ({self.transaction_hash})"
