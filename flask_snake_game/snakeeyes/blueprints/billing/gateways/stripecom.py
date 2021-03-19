import stripe 

class Plan(object):
	@classmethod
	def retrieve(cls, plan):
		"""Retrieve an existing plan ."""
		try:
			return stripe.Plan.retrieve(paln)
		except stripe.error.StripeError as e:
			print (e)

	@classmethod
	def list(cls):
		"""List all existing plan"""
		try:
			return stripe.Plan.all()
		except stripe.error.StripeError as e:
			print(e)

	@classmethod
	def create(cls, id = None, name = None, amount = None, 
		     currency = None, interval = None, interval_count = None, trial_period_days = None,
		     statement_descriptor = None, metadata = None):
		"""Create new subscriptions plan"""


		try:
			return stripe.Plan.create(id= id,
									  name = name,
									  amount = amount,
									  currency = currency,
									  interval = interval,
									  interval_count = interval_count,
									  trial_period_days = trial_period_days,
									  metadata = metadata, 
									  statement_descriptor = statement_descriptor
									  )

		except stripe.error.StripeError as e:
			print(e)


	@classmethod
	def update(cls, id = None, name = None, metadata = None, 
				statement_descriptor = None):
		"""Update exixting subscription plan """
		try:
			plan = stripe.Plan.retrieve(id)

			plan.name = name 
			plan.metadata = metadata
			plan.statement_descriptor = statement_descriptor
			return plan.save()
		except stripe.error.StripeError as e:
			print(e)


	@classmethod
	def delete(cls, plan):
		"""Delete an existing plan"""
		try:
			plan = stripe.Plan.retrieve(plan)
			return plan.delete()
		except stripe.error.StripeError as e:
			print(e)