import sys
import os
import pygraphviz as pgv
import operator

should_draw_colors=True
project_path=''
diagram_file='modules_diagram.png'

def get_modules():
	dirs=filter(__filter_directory, os.listdir(project_path))
	return filter(__filter_build_gradle, dirs)

def generate_diagrams(modules):
	return dict(map(__add_dependencies, modules))

def generate_color_edges(modules):
	edge_api=reduce(operator.add, map(__add_api_edges, modules))
	edges_implementation=reduce(operator.add, map(__add_implememntation_edges, modules))
	return (edge_api, edges_implementation)

def __filter_directory(x):
	return os.path.isdir(os.path.join(project_path,x))

def __filter_build_gradle(x):
	return 'build.gradle' in  os.listdir(project_path + "/" + x)

def __add_dependencies(x):
	module_path=os.path.join(project_path,x)
	build_gradle=open(os.path.join(module_path,'build.gradle'), 'r')
	readlines=build_gradle.readlines()
	dependencies=map(__clean_up, filter(__filter_all_dependencies, readlines))
	return [x, dict(zip(dependencies,len(dependencies)*[None]))]

def __add_api_edges(x):
	module_path=os.path.join(project_path,x)
	build_gradle=open(os.path.join(module_path,'build.gradle'), 'r')
	readlines=build_gradle.readlines()
	return map(lambda y: (x, __clean_up(y)), filter(__filter_api_dependencies, readlines))

def __add_implememntation_edges(x):
	module_path=os.path.join(project_path,x)
	build_gradle=open(os.path.join(module_path,'build.gradle'), 'r')
	readlines=build_gradle.readlines()
	return map(lambda y: (x, __clean_up(y)), filter(__filter_implementation_dependencies, readlines))

def __filter_all_dependencies(x):
	x_no_blank=x.strip().replace(" ", "")
	return (not x_no_blank.startswith("//"))\
	    and ('compileproject' in x_no_blank\
		or 'implementationproject' in x_no_blank\
		or 'apiproject' in x_no_blank)

def __filter_api_dependencies(x):
	x_no_blank=x.strip().replace(" ", "")
	return (not x_no_blank.startswith("//"))\
	    and ('compileproject' in x_no_blank\
		or 'apiproject' in x_no_blank)

def __filter_implementation_dependencies(x):
	x_no_blank=x.strip().replace(" ", "")
	return (not x_no_blank.startswith("//"))\
	    and ('implementationproject' in x_no_blank)
	
def __clean_up(x):
	return x.strip().replace(" ", "")\
		.replace("compileproject","")\
		.replace("implementationproject","")\
		.replace("apiproject","")\
		.replace("(","")\
		.replace(")","")\
		.replace("'","")\
		.replace("\"","")\
		.replace(":","")\
		.replace("path","")
	
def generate_graph(graph_data):
	graph = pgv.AGraph(graph_data, directed=True)
	graph.layout(prog='dot')
	return graph

def draw_colors(graph, edges_api_data, eges_implementation_data):
	for edge_data in edges_api_data:
		graph.get_edge(edge_data[0], edge_data[1]).attr['color']='red'

	for edge_data in eges_implementation_data:
		graph.get_edge(edge_data[0], edge_data[1]).attr['color']='blue'

def draw_graph(graph):
	graph.draw(diagram_file)
	print "Saved in: %s" % diagram_file

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Missing project path"
	else:
		project_path=sys.argv[1]
		if len(sys.argv) == 3:
			graph_name=sys.argv[2]

		modules=get_modules()
		
		graph_data=generate_diagrams(modules)
		graph=generate_graph(graph_data)

		if should_draw_colors:
			(edges_api_data, eges_implementation_data)=generate_color_edges(modules)
			draw_colors(graph, edges_api_data, eges_implementation_data)
			graph.graph_attr['label']="Api/Compile: Red\nImplementation: Blue"

		draw_graph(graph)
