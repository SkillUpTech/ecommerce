from django import template
register = template.Library()

@register.filter
def replace_commas(string):
	return string.replace('with professional certificate', '(Live-Online) with verified certificate and 1 hour of instructor support').replace('Seat in', '').replace('with verified certificate (and ID verification)', '(Live-Online) with verified certificate and 1 hour of instructor support.')

