__version__ = "0.0.1"

from erpnext.accounts.doctype.budget import budget
from beams.beams.overrides.budget import validate_expense_against_budget

budget.validate_expense_against_budget = validate_expense_against_budget
