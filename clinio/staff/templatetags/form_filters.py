from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css})
    return field 
