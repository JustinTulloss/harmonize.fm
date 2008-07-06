"""Dictionaries of sizes for single objects and object types.
The values of the dictionaries can be called with an object to construct
a wrapper.

It deliberately does nothing so that anything interested can register
something."""

# First, rules for single objects. These are the highest precedence.
# Keys are object ID.
object = {}

# Next, rules for specific types. Keys can be type, type ID or type string
# of the form module.type.
# These rules are mostly useless to register outside of the scanner,
# since it will not consider them when counting subclasses.
wholetype = {}

# Rules for specific types excluding their supertypes. When using this,
# the scanner will add the type's superclasses itself.
type = {}

# Finally, rules for types or their subclasses. Keys can be type, type ID or
# type string of the form module.type.
# Mostly used to mark objects as special by deriving them from a particular
# class. wrappers.ignored is registered here.
instance = {}

# Sample objects of each type.
samples = {}
