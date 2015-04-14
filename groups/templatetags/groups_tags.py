from django import template


register = template.Library()


@register.simple_tag
def comment_render(comment, request):
    return comment.render(request)
