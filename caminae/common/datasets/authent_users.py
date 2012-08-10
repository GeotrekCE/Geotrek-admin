from . import BaseSetup
from caminae.authent.fixtures.development import populate_users

class Setup(BaseSetup):

    requires = ('authent_groups', )

    def run(self):
       user_profiles = populate_users()
       if self.verbosity > 1:
           for up in user_profiles:
               self.print_indent(
                    "Created user %s (lang: %s) with groups: %s)" % (
                       up.user.username, up.language, up.user.groups.all()
                ))
