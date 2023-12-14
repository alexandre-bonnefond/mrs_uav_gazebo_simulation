#!/usr/bin/python3
import atexit
import sys
import rospkg
import math
import xml.dom.minidom
from inspect import getmembers, isfunction
from jinja2 import meta
from datatypes import TemplateWrapper

import jinja_utils

glob_running_processes = []

# #{ exit_handler
def exit_handler():
    print('[INFO] [MrsDroneSpawner]: Exit requested')

    if len(glob_running_processes) > 0:
        print(f'[INFO] [MrsDroneSpawner]: Shutting down {len(glob_running_processes)} subprocesses')

        num_zombies = 0
        for p, pid in glob_running_processes:
            try:
                p.shutdown()
                print(f'[INFO] [MrsDroneSpawner]: Process {pid} shutdown')
            except:
                num_zombies += 1

        if num_zombies > 0:
            print(f'\033[91m[ERROR] [MrsDroneSpawner]: Could not stop {num_zombies} subprocesses\033[91m')
            exit(1)

    print('[INFO] [MrsDroneSpawner]: Exited gracefully')
    exit(0)
# #}

class MrsDroneSpawner:

    def __init__(self, show_help=False, verbose=False):

        self.verbose = verbose
        self.rospack = rospkg.RosPack()


        self.resource_paths = []
        self.resource_paths.append(self.rospack.get_path('mrs_uav_gazebo_simulation'))
        self.resource_paths.append(self.rospack.get_path('external_gazebo_models'))

        # self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.resource_paths))
        self.jinja_env = jinja_utils.configure_jinja2_environment(self.resource_paths)

        print('Jinja templates available:')
        print([t.filename for t in jinja_utils.get_all_templates(self.jinja_env)])
        print('------------------------')

        # load all available models
            # from current package
            # from external packages (multiple)

        # compose all available params

        # display help (params) for individual models

    def extract_jinja_params(self, model_name):
        for n in self.jinja_env.list_templates(filter_func=jinja_utils.filter_templates):
            if model_name in n:
                template_filepath = self.jinja_env.get_template(n).filename
                with open(template_filepath, 'r') as f:
                    content = f.read()
                    parsed_content = self.jinja_env.parse(content)
                    macros = [node.name for node in parsed_content.find_all(meta.Macro)]
                    print(macros)
                    # variable_names = meta.find_undeclared_variables(parsed_content)
                    # used_subtemplates = meta.find_referenced_templates(parsed_content)
                    # return sorted(variable_names)

    def render(self, model_name, output):
        for tw in jinja_utils.build_template_hierarchy(self.jinja_env):
            if model_name in tw.jinja_template.filename:
                spawner_args = {
                    "enable_component_with_args": [0.01, 0.38],
                    "enable_second_order_component": None,
                    "enable_third_order_component": None,
                }

                params = {
                    "spawner_args": spawner_args
                #     "name": "uav1",
                #     "namespace": "uav1",
                #     "enable_rangefinder": True,
                #     "enable_component": True,
                #     "spawner_args": {'roll': 0.1, 'pitch': 0.1}
                          }
                context = tw.jinja_template.new_context(params)
                rendered_template = tw.jinja_template.render(context)
                root = xml.dom.minidom.parseString(rendered_template)
                ugly_xml = root.toprettyxml(indent='  ')
                # Remove empty lines
                pretty_xml = "\n".join(line for line in ugly_xml.split("\n") if line.strip())
                with open(output, 'w') as f:
                    f.write(pretty_xml)


if __name__ == '__main__':

    print('[INFO] [MrsDroneSpawner]: Starting')
    
    show_help = 'no_help' not in sys.argv
    verbose = 'verbose' in sys.argv

    atexit.register(exit_handler)

    try:
        spawner = MrsDroneSpawner(show_help, verbose)

        loaded_templates = []

        jinja_utils.build_template_hierarchy(spawner.jinja_env)

        # for t in jinja_utils.get_all_templates(spawner.jinja_env):
        #     # print('Template:', t)

        #     imports = jinja_utils.get_imported_templates(spawner.jinja_env, t)
        #     macros = jinja_utils.get_macros_from_template(spawner.jinja_env, t)
        #     # for macro_name, component in macros.items():
        #     #     print('\tMacro:', macro_name)
        #     #     print('\t\tKeyword:', component.keyword)
        #     #     print('\t\tDescription:', component.description)
        #     #     print('\t\tDefaultArgs:', component.default_args)
        #     # # print(macros)
        #     # print()
            
        #     template_wrapper = TemplateWrapper(t, imports, macros)
        #     loaded_templates.append(template_wrapper)



        # for temp in loaded_templates:
        #     print('Template:', temp.jinja_template)
        #     print('\tImports:')
        #     for imported_template in temp.imported_templates:
        #         print('\t\t', imported_template)

        #     print('\tMacros:')
        #     for macro_name, component in temp.components.items():
        #         print('\t\tMacro:', macro_name)
        #         print('\t\t\tKeyword:', component.keyword)
        #         print('\t\t\tDescription:', component.description)
        #         print('\t\t\tDefaultArgs:', component.default_args)


        # # params = jinja_utils.get_all_params('x555', spawner.jinja_env)
        # # params = jinja_utils.get_all_params('f400', spawner.jinja_env)
        # # print(params)
        # # spawner.render('x555', '/home/mrs/devel_workspace/src/external_gazebo_models/models/x555/sdf/x555.sdf')
        # # spawner.render('f400', '/home/mrs/devel_workspace/src/external_gazebo_models/models/f400/sdf/f400.sdf')
        spawner.render('dummy', '/home/mrs/devel_workspace/src/external_gazebo_models/dummy.sdf')
    except rospy.ROSInterruptException:
        pass
