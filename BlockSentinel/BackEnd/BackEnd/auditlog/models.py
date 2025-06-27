from django.db import models
from django.conf import settings  # ✅ Use this instead of direct import from auth
import uuid

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

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MonitoredEvent(models.Model):
    SYSTEM = 'SYSTEM'
    DATABASE = 'DATABASE'
    AGENT = 'AGENT'
    SOURCE_CHOICES = [
        (SYSTEM, 'System'),
        (DATABASE, 'Database'),
        (AGENT, 'Agent'),
    ]

    INFO = 'INFO'
    WARNING = 'WARNING'
    CRITICAL = 'CRITICAL'
    SEVERITY_CHOICES = [
        (INFO, 'Info'),
        (WARNING, 'Warning'),
        (CRITICAL, 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    system_id = models.CharField(max_length=100, db_index=True)
    user = models.CharField(max_length=150, null=True, blank=True)  # Username or identifier performing action
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=AGENT)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default=INFO)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} | {self.system_id} | {self.event_type} | {self.severity}"

class AnomalyEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    system_id = models.CharField(max_length=100)
    user = models.CharField(max_length=150, null=True, blank=True)
    event_type = models.CharField(max_length=100)  # e.g., SQL Injection, Unauthorized Access
    description = models.TextField()
    severity = models.CharField(max_length=20, default="CRITICAL")
    source = models.CharField(max_length=50, default="AnomalyEngine")
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.event_type} on {self.system_id}"