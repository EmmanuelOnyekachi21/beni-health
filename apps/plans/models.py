from django.db import models
import uuid
# Create your models here.
class Plan(models.Model):
    """
    An insurance plan defines what's covered, limits and rules.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Coverage limits (stored as JSON)
    annual_cap = models.DecimalField (max_digits=12, decimal_places=2)
    visit_cap = models.IntegerField()  # max visits per year
    covered_services = models.JSONField()  # list of service codes
    co_pay_rules = models.JSONField()  # copay amounts for different services
    
    referral_required = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plans'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.plan_code} - {self.name}"


