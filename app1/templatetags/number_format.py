from django import template

register = template.Library()

@register.filter
def indian_compact(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    if value >= 1_00_00_000:
        return f"{value/1_00_00_000:.1f}Cr"
    elif value >= 1_00_000:
        return f"{value/1_00_000:.1f}L"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    return str(int(value))
