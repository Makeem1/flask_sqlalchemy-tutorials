from flask import Blueprint, redirect, url_for, flash, render_template, request, current_app
from config import settings 
from snakeeyes.blueprints.billing.decorators import handle_stripe_exceptions, subscription_required
from snakeeyes.blueprints.billing.models.subscription import Subscription
from flask_login import login_required, current_user
from snakeeyes.blueprints.billing.forms import CreditCardForm, \
    UpdateSubscriptionForm, CancelSubscriptionForm

billing = Blueprint('billing', __name__, template_folder = '../templates', url_prefix = '/subscription')


@billing.route('/pricing')
def pricing():
	if current_user.is_authenticated and current_user.subscription:
		return redirect(url_for('billing.update'))

	form = UpdateSubscriptionForm()

	return render_template('billing/pricing.html', form=form, plans=settings.STRIPE_PLANS)


@billing.route('/create', methods=['GET', 'POST'])
# @handle_stripe_exceptions
# @login_required
def create():
	if current_user.subscription:
		flash("You already have an active subscription.", 'info')
		return redirect(url_for('user.settings'))

	plan = request.args.get('plan')
	subscription_plan = Subscription.get_plan_by_id(plan)

	if subscription_plan is None and request.method == "GET":
		flash('Sorry, that plan did not exist.', 'error')
		return redirect(url_for('billing.pricing'))

	stripe_key = create_app.config.get('STRIPE_PUBLISHABLE_KEY')
	form = CreditCardForm(stripe_key=stripe_key, plan = plan )

	if form.validate_on_submit():
		subscription = Subscription()
		created = subscription.create(user=current_user,
									  name = request.form.get('name'),
									  plan = request.form.get('plan'),
									  coupon = request.form.get('coupon_code'),
									  token = request.form.get('stripe_token'))

		if created:
			flash('Awesome, thanks for subscribing!', 'success')
		else:
			flash('You must enable Javascript for this request.', 'warning')

		return redirect(url_for('user.settings'))

	return render_template('billing/payment_method.html', form = form , plan = subscription_plan)


@billing.route('/update_pyament_method', methods=['GET', 'GET'])
# @handle_stripe_exceptions
# @login_required
def update_payment_method():
	if not current_user.credit_card:
		flash('You do not have a payment method on file.', 'error')
		return redirect(url_for('user.settings'))


	active_plan = Subscription.get_plan_by_id(current_user.subscription.plan)

	card = current_user.credit_card
	stripe_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY')
	form = CreditCardForm(stripe_key=stripe_key,
                          plan=active_plan,
                          name=current_user.name)

	if form.validate_on_submit():
		subscription = Subscription()
		updated = subscription.update_payment_method(user=current_user, 
        												credit_card=card, 
        												name=request.form.get('name'), 
        												token=request.form.get('stripe_token'))

		if updated():
			flash('Your payment method has been updated.', 'success')
		else:
			flash('You must enable Javascript for this process', 'warning')

		return redirect(url_for('user.settings'))

	return render_template('billing/payment_method.html', form = form , plan = active_plan, card_last4=str(card.last4))


@billing.route('/update', methods=['GET', 'POST'])
# @handle_stripe_exceptions
# @subscription_required
# @login_required
def update():
	current_plan = current_user.subscription
	active_plan = Subscription.get_plan_by_id(current_plan)
	new_plan = Subscription.get_new_plan(request.form.keys())

	plan = Subscription.get_plan_by_id(new_plan)

	is_same_plan = new_plan == active_plan['id']

	if ((new_plan is not None and plan is None) or is_same_plan) and request.method == 'POST':
		return redirect(url_for('billing.update'))

	form = UpdateSubscriptionForm(coupon_code = current_user.subscription.coupon)

	if form.validate_on_submit():
		subscription = Subscription()
		updated = subscription.update(user=current_user, coupon=request.form.get('coupon_code'), plan=plan.get('id'))


		if updated:
			flash('Your subscription has been updated.', 'success')
			return redirect(url_for(user.settings))

	return render_template('billing/pricing.html', form = form , plan = settings.STRIPE_PLANS, active_plan = active_plan)