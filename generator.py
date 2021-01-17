import functools
import itertools
import multiprocessing
import operator
import os
import pygraphviz as pgv
import sys

project_path = ''
file_directory = 'modules_diagram'

def get_modules():
    dirs = filter(__filter_directory, os.listdir(project_path))
    return filter(__filter_build_gradle, dirs)

def generate_diagrams(modules):
    return dict(map(__add_dependencies, modules))

def __filter_directory(x):
    return os.path.isdir(os.path.join(project_path, x))

def __filter_build_gradle(x):
    return 'build.gradle' in os.listdir(project_path + "/" + x)

def __add_dependencies(x):
    module_path = os.path.join(project_path, x)
    build_gradle = open(os.path.join(module_path, 'build.gradle'), 'r')
    readlines = build_gradle.readlines()
    dependencies = map(__clean_up, filter(__filter_all_dependencies, readlines))
    return [x, dict(zip(dependencies, len(dependencies) * [None]))]

def __add_api_edges(x):
    module_path = os.path.join(project_path, x)
    build_gradle = open(os.path.join(module_path, 'build.gradle'), 'r')
    readlines = build_gradle.readlines()
    return map(lambda y: (x, __clean_up(y)), filter(__filter_api_dependencies, readlines))

def __add_implementation_edges(x):
    module_path = os.path.join(project_path, x)
    build_gradle = open(os.path.join(module_path, 'build.gradle'), 'r')
    readlines = build_gradle.readlines()
    return map(lambda y: (x, __clean_up(y)),
               filter(__filter_implementation_dependencies, readlines))

def __filter_all_dependencies(x):
    x_no_blank = x.strip().replace(" ", "")
    return (not x_no_blank.startswith("//")) \
           and ('compileproject' in x_no_blank \
                or 'implementationproject' in x_no_blank \
                or 'apiproject' in x_no_blank)

def __filter_api_dependencies(x):
    x_no_blank = x.strip().replace(" ", "")
    return (not x_no_blank.startswith("//")) \
           and ('compileproject' in x_no_blank \
                or 'apiproject' in x_no_blank)

def __filter_implementation_dependencies(x):
    x_no_blank = x.strip().replace(" ", "")
    return (not x_no_blank.startswith("//")) \
           and ('implementationproject' in x_no_blank)

def __clean_up(x):
    return x.strip().replace(" ", "") \
        .replace("compileproject", "") \
        .replace("implementationproject", "") \
        .replace("apiproject", "") \
        .replace("(", "") \
        .replace(")", "") \
        .replace("'", "") \
        .replace("\"", "") \
        .replace(":", "") \
        .replace("path", "") \
        .replace(",configurationdefault", "")

def __resolve_dependencies(graph_data, module_list, aggregate):
    aggregate += module_list
    dependency_modules = list(itertools.chain(*map(lambda x: graph_data[x].keys(), module_list)))
    if len(dependency_modules) == 0:
        return aggregate
    return __resolve_dependencies(graph_data, dependency_modules, aggregate)


def generate_graph(graph_data):
    graph = pgv.AGraph(graph_data, directed=True)
    graph.layout(prog='dot')
    return graph

def draw_graph(all_modules_graph_data, module):
    selected_modules = __resolve_dependencies(all_modules_graph_data, [module], [])
    graph = generate_graph(generate_diagrams(selected_modules))

    api_edges = functools.reduce(operator.iconcat, map(__add_api_edges, selected_modules), [])
    implementation_edges = functools.reduce(operator.iconcat, map(__add_implementation_edges, selected_modules), [])

    for edge in api_edges:
        graph.get_edge(edge[0], edge[1]).attr['color'] = 'red'

    for edge in implementation_edges:
        graph.get_edge(edge[0], edge[1]).attr['color'] = 'blue'

    graph.graph_attr['label'] = "Api/Compile: Red\nImplementation: Blue"

    file_name = "%s/%s.png" % (file_directory, module)

    graph.draw(file_name)
    print "Saved in: %s" % file_name

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Missing project path"
    else:
        project_path = sys.argv[1]
        if len(sys.argv) == 3:
            graph_name = sys.argv[2]

    try:
        os.mkdir(file_directory)
    except OSError:
        print "Could not create %s directory" % file_directory

    modules = sorted(get_modules())
    all_modules_graph_data = generate_diagrams(modules)

    jobs = []
    for module in modules:
        job = multiprocessing.Process(target=draw_graph, args=(all_modules_graph_data, module,))
        jobs.append(job)
        job.start()

    for job in jobs:
        job.join()