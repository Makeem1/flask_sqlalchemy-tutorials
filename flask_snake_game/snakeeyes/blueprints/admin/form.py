from collections import OrderedDict

from flask_wtf import Form
from wtforms import (StringField, SelectField, BooleanField,
                    IntegerField, FloatField, SelectField, DateTimeField)
from wtforms.validators import DataRequired, Length, Regexp, Optional, NumberRange
from wtforms_components import Unique
from lib.utils_wtforms import ModelForm, choices_from_dict

from snakeeyes.blueprints.user.models import db, User
from snakeeyes.blueprints.billing.models.coupon import Coupon

from lib.locale import Currency


class SearchForm(Form):
	search = StringField('Search terms', validators=[Optional(), Length(min=4, max=128, message='Limit your search text.')])
	

class BulkDeleteForm(Form):
    SCOPE = OrderedDict([
        ('all_selected_items', 'All selected items'),
        ('all_search_results', 'All search results')
    ])

    scope = SelectField('Privileges', [DataRequired()],
                        choices=choices_from_dict(SCOPE, prepend_blank=False))


class UserForm(ModelForm):
    username_message = 'Letters, numbers and underscores only please.'

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session
        ),
        Optional(),
        Length(1, 16),
        # Part of the Python 3.7.x update included updating flake8 which means
        # we need to explicitly define our regex pattern with r'xxx'.
        Regexp(r'^\w+$', message=username_message)
    ])
    coins = StringField('coins', validators=[DataRequired(), Length(min=1, max=234567812 )])

    role = SelectField('Privileges', [DataRequired()],
                       choices=choices_from_dict(User.ROLE,
                                                 prepend_blank=False))
    active = BooleanField('Yes, allow this user to sign in')

class UserCancelSubscriptionForm(Form):
    pass

class CouponForm(Form):
    percent_off = IntegerField('Percent of (%)',
                                validators=[Optional(), NumberRange(min=1, max=100)])
    amount_off = FloatField('Amount off ($)', 
                                validators=[Optional(), NumberRange(min=0.01, max=21474836.0)])
    
    code = StringField('Code', 
                            validators=[DataRequired(), Length(min=1, max=32)])
    
    currency = SelectField('Currency', validators=[DataRequired()], 
                            choices=choices_from_dict(Currency.TYPES, prepend_blank=False))
    
    duration = SelectField('Duaration', 
                            validators=[DataRequired()], 
                            choices=choices_from_dict(Coupon.DURATION, prepend_blank=False))
    
    duration_in_months = IntegerField('Duration', 
                        validators=[Optional(), NumberRange(min=1, max=12) ])
    
    max_redemptions = IntegerField('Max Redeemptions', 
                                    validators=[Optional(), NumberRange(min=1, max=2147483647)])
    
    redeem_by = DateTimeField('Redeem by', 
                                validators=[Optional()], format='%Y-%m-%d %H:%M:%S')

    def validate(self):
        if not Form.validate(self):
            return False

        result = True

        percent_off = self.percent_off.data
        amount_off = self.amount_off.data

        if percent_off is None and amount_off is None:
            empty_error = 'Pick atleast one.'
            self.percent_off.errors.append(empty_error)
            self.amount_off.errors.append(empty_error)
            result = False
        elif percent_off and amount_off:
            both_error = 'Cannot pick both'
            self.percent_off.errors.append(both_error)
            self.amount_off.errors.append(both_error)

            return False
        else:
            pass


        return result
