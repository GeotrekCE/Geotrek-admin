from django import template
from django.conf import settings
from django.template import Context
from django.template.base import TemplateDoesNotExist


register = template.Library()


class SmartIncludeNode(template.Node):
    def __init__(self, object, viewname):
        self.object = object
        self.viewname = viewname

    def render(self, context):
        apps = [app.split('.')[-1] for app in settings.INSTALLED_APPS]
        modelname = context[self.object]._meta.object_name.lower()
        viewname = self.viewname
        result = ""
        for module in apps:
            try:
                t = template.loader.get_template("%(module)s/%(modelname)s_%(module)s_%(viewname)s.html" % locals())
                result += t.render(context)
            except TemplateDoesNotExist:
                pass
        return result

@register.tag(name="smart_include")
def do_smart_include(parser, token):
    try:
        tag_name, object, viewname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires two arguments" % token.contents.split()[0])
    if not (viewname[0] == viewname[-1] and viewname[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's viewname argument should be in quotes" % tag_name)
    return SmartIncludeNode(object, viewname[1:-1])
