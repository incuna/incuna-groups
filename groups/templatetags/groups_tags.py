from django import template


register = template.Library()


@register.simple_tag
def comment_render(comment, request):
    """Render the comment template in the view."""
    return comment.render(request)
