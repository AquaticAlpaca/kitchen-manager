# A list of domain-specific terms with their definitions

This glossary exists to:

- ensure that human and AI developers have a shared understanding about the
  terms used in the repo
- allow human and AI developers to refer to difficult or complex concepts
  concisely

This is a living document. When you find a discrepancy between a human's use of
a term and the glossary, first:

- Question the human about the discrepancy until a shared understanding is
  reached, then
- Update the glossary to reflect the new understanding

## Terms and their definitions

Pantry: a digital representation of the contents of the user's physical pantry,
refrigerator, and freezer. This is the source of truth for the application; the
other features (like meal planner and shopping list) increment or decrement the
quantity of items in the pantry.

Shopping list: a digital representation of things the user wants to buy. Items
may be added to the shopping list manually, or automatically via a planned meal,
or via a feature that automatically reorders pantry items that are under
stocked.

Meal plan: a way for the home cook to plan upcoming meals. Each meal plan
consists of a meal and a date. Users may view meal plans on a calender, or in a
detail view.

Meal: A collection of ingredients which can be stored in the database for later
use, or can be scheduled via a meal plan.

Ingredients: Specific quantities of pantry items which, when used together, make
a meal.

User: A home cook, a shopper, or a household member who wants to plan meals,
view meal plans, or shop for grocieries. Each user is part of a household.

Household: All of the people in a house who make, plan, or shop for food and
want to track their activities via the app. A household must have at least one
user.

Canonical units: A way to measure the quantity of each item as it it sold in the
store. Different items have different canonical units depending on the type of
item and the household's unit system.

- Example 1: Flour is sold in pounds (imperial) or grams (metric).
- Example 2: Milk is sold in gallons (imperial) or liters (metric).
- Example 3: Eggs are sold in dozens.

Cooking units: A translation of canonical units into the unit used by an
ingredient in a recipe.

- Example 1: Flour's canonical unit is pounds (imperial), but for cooking it is
  measured in cups (imperial).
- Example 2: Milk's canonical unit is gallons (imperial), but for cooking it is
  measured in cups (imperial).
- Example 3: Eggs canonical units are dozens, but for cooking they are measured
  in pieces (eg: 2 eggs)

Items: The basic unit of data in the app. Items represent a single grocery or
household item and its quantity.
