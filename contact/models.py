from django.db import models


class ContactSubmission(models.Model):
	DELIVERY_PENDING = 'pending'
	DELIVERY_SENT = 'sent'
	DELIVERY_FAILED = 'failed'

	DELIVERY_STATUS_CHOICES = [
		(DELIVERY_PENDING, 'Pending'),
		(DELIVERY_SENT, 'Sent'),
		(DELIVERY_FAILED, 'Failed'),
	]

	name = models.CharField(max_length=255)
	email = models.EmailField()
	mobile = models.CharField(max_length=64)
	service = models.CharField(max_length=255)
	delivery_status = models.CharField(
		max_length=20,
		choices=DELIVERY_STATUS_CHOICES,
		default=DELIVERY_PENDING,
	)
	delivery_error = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.name} <{self.email}> ({self.delivery_status})'


