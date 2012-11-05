from django import template
from django.conf import settings
from django.template import Context
from django.template.base import TemplateDoesNotExist


register = template.Library()


class SmartIncludeNode(template.Node):
    def __init__(self, viewname):
        self.viewname = viewname

    def render(self, context):
        apps = [app.split('.')[-1] for app in settings.INSTALLED_APPS]
        viewname = self.viewname
        result = ""
        for module in apps:
            try:
                t = template.loader.get_template("%(module)s/%(module)s_%(viewname)s_fragment.html" % locals())
                result += t.render(context)
            except TemplateDoesNotExist:
                pass
        return result

@register.tag(name="smart_include")
def do_smart_include(parser, token):
    try:
        tag_name, viewname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires one argument" % token.contents.split()[0])
    if not (viewname[0] == viewname[-1] and viewname[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's viewname argument should be in quotes" % tag_name)
    return SmartIncludeNode(viewname[1:-1])
