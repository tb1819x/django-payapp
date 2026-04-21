from django.db import models
from django.contrib.auth.models import User
from .thrift_client_helper import get_remote_timestamp
from datetime import datetime

class Account(models.Model):
	"""
	This class represents a users financial account within the system

	This model stores account specific data such as balance and currency,
	and is linked to the Django User model for authentication purposes.
	"""
	user = models.ForeignKey(User, on_delete=models.CASCADE) 
	balance = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=10)

class Transaction(models.Model):
	"""
	This class represents a record i.e a single transaction

	The model stores the amount to be sent, 
	the sender and the receiver, and time/date sent
	"""
	timestamp = models.BigIntegerField(blank=True, null=True)

	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="money_out_transactions")
	receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="money_in_transactions")
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	
	#Function for saving a timestamp using the thrift service whenever a transaction is saved
	def save(self, *args, **kwargs):
		if not self.timestamp:
			self.timestamp = get_remote_timestamp()
		super().save(*args, **kwargs)
	
	def get_readable_timestamp(self):
		#A try added to handle previous transaction timestamps which are already strings before thrift services was created
		#Duplicated this version and used flushed to clear data to start again. so no need for try
		try:
			return datetime.fromtimestamp(int(self.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
		except (TypeError, ValueError):
			return str(self.timestamp)

class PaymentRequest(models.Model):
	"""
	This class represents a payment request between users, seperating intent from actual 
	transactions.
	
	The model stores request specific data such as requester 
	and recipient, status, amount, time/date
	"""
	requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_request_sent")
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_request_received")
	status = models.CharField(max_length=10,
						   choices=[
							   ("pending", "Pending"),
							   ("accepted", "Accepted"),
							   ("rejected", "Rejected")
						   ],
						   default="pending")
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	timestamp = models.DateTimeField(auto_now_add=True)

