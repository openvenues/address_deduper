import pkgutil

from address_normalizer.views.base import *

for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = module

def init_views(app):
	for key, view in view_registry.iteritems():
		app.register_blueprint(view.blueprint)