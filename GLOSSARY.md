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

Pantry: A digital representation of the contents of the user's physical pantry,
refrigerator, and freezer. The pantry is the **source of truth** for the
application; other features (meal planner, shopping list) modify pantry
quantities when actions are completed. Pantry items are stored in their
canonical units.

**See also:** [System Behaviors](#system-behaviors): _Meal preparation, Shopping
completion, Stock threshold monitoring_

Shopping list: a digital representation of things the user wants to buy. Items
may be added to the shopping list manually, or automatically via a planned meal,
or via a feature that automatically reorders pantry items that are under
stocked.

**See also:** [System Behaviors](#system-behaviors): _Shopping completion, Stock
threshold monitoring_

Meal plan: A way for the home cook to plan upcoming meals. Each meal plan
consists of a meal scheduled for a specific date. When a meal plan is created,
its ingredients are automatically added to the shopping list. When a meal plan
is marked as prepared, its ingredients are deducted from the pantry. Users may
view meal plans on a calendar or in detail.

**See also:** [System Behaviors](#system-behaviors): _Meal preparation_

Meal: A collection of ingredients which can be stored in the database for later
use, or can be scheduled via a meal plan.

Ingredients: Specific quantities of pantry items which, when used together, make
a meal.

User: A home cook, a shopper, or a household member who wants to plan meals,
view meal plans, or shop for groceries. Each user is part of a household.

Household: All of the people in a house who make, plan, or shop for food and
want to track their activities via the app. A household must have at least one
user. In the system, each household is identified by a unique `household_id`.
Data is scoped to households via row-level security (RLS), ensuring users can
only access their own household's data.

**See also:** [System Behaviors](#system-behaviors): _User authentication_

Canonical unit: A way to measure the quantity of each item as it is sold in
stores. Different items have different canonical units depending on the type of
item and the household's unit system. Canonical units are the primary unit of
measurement for items in the pantry and shopping list.

- Example 1: Flour is sold in pounds (imperial) or grams (metric).
- Example 2: Milk is sold in gallons (imperial) or liters (metric).
- Example 3: Eggs are sold by count.

Cooking unit: A unit of measurement used in recipes to specify ingredient
quantities. Cooking units are a translation of canonical units into more
practical measurements for cooking.

- Example 1: Flour's canonical unit is pounds (imperial), but for cooking it is
  measured in cups (imperial).
- Example 2: Milk's canonical unit is gallons (imperial), but for cooking it is
  measured in cups (imperial).
- Example 3: Eggs canonical units are count and for cooking they are measured in
  count (eg: 2 eggs)

Unit conversion: A mapping that defines how to convert between a canonical unit
and a cooking unit for a specific ingredient. Because different ingredients have
different densities, conversions are ingredient-specific. Example: "1 pound of
flour = 3.6 cups" (all-purpose flour).

Household unit system: the system of measurements that a household uses. Choices
are "imperial" or "metric".

Stock threshold: A configurable minimum quantity for a pantry item. When a
pantry item's quantity falls below its stock threshold, the system automatically
adds the deficit to the shopping list.

Shopping list item source: The origin of a shopping list item. Sources can be:
(1) manual addition by a shopper, (2) automatic addition from a planned meal, or
(3) automatic addition from a stock threshold being breached.

Items: The basic unit of data in the app. Items represent a type of grocery or
household item (e.g., 'flour', 'milk', 'spinach'). Items belong to a household
and have a canonical unit. Quantities of items are tracked separately in the
pantry, shopping list, and meal ingredients. All data is scoped to a
`household_id` and protected by row-level security (RLS). Users can export their
household's data at any time (user ownership principle).

## System Behaviors

Meal preparation: When a user marks a meal plan as prepared, the system deducts
all meal ingredients from the pantry in their canonical units. Preparation can
only occur on or after the meal's scheduled date.

Shopping completion: When a shopping list item is marked as purchased, it is
immediately moved to the pantry (in its canonical unit) and removed from the
shopping list. The shopping list item's sources are preserved for reference.

Stock threshold monitoring: When a pantry item's quantity falls below its stock
threshold, the system automatically adds the deficit to the shopping list. This
behavior triggers the automatic reorder feature.

Data synchronization: Changes made to pantry items, shopping lists, and meal
plans are synchronized across devices using Supabase Realtime. The app is
offline-first, with @tanstack/react-query + SQLite caching local data for use
without internet connectivity.

User authentication: Users authenticate via Supabase using magic link, biometric
auth, or passphrase. Upon authentication, users are assigned to a household and
gain access to household-scoped data (pantry, shopping lists, meal plans).
