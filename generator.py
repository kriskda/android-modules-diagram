import sys
import os
import pygraphviz as pgv

project_path=''
graph_name=''
diagram_file='modules_diagram.png'

def generate_diagrams():
	dirs=filter(__filter_directory, os.listdir(project_path))
	modules=filter(__filter_build_gradle, dirs)
	return dict(map(__add_dependencies, modules))
	
def __filter_directory(x):
	return os.path.isdir(os.path.join(project_path,x))

def __filter_build_gradle(x):
	return 'build.gradle' in  os.listdir(project_path + "/" + x)

def __add_dependencies(x):
	module_path=os.path.join(project_path,x)
	build_gradle=open(os.path.join(module_path,'build.gradle'), 'r')
	dependencies=map(__clean_up, filter(__filter_dependencies, build_gradle.readlines()))
	return [x, dict(zip(dependencies,len(dependencies)*[None]))]

def __filter_dependencies(x):
	x_no_blank=x.strip().replace(" ", "")
	return 'compileproject' in x_no_blank\
		or 'testCompileproject' in x_no_blank\
		or 'implementationproject' in x_no_blank\
		or 'testImplementationproject' in x_no_blank
	
def __clean_up(x):
	return x.strip().replace(" ", "")\
		.replace("compileproject","")\
		.replace("testCompileproject","")\
		.replace("implementationproject","")\
		.replace("testImplementionproject","")\
		.replace("(","")\
		.replace(")","")\
		.replace("'","")\
		.replace("\"","")\
		.replace(":","")\
		.replace("path","")
	
def generate_graph(graph_data):
	graph = pgv.AGraph(graph_data, directed=True)
	graph.graph_attr['label']=graph_name
	graph.layout(prog='dot')
	graph.draw(diagram_file)
	print "Saved in: %s" % diagram_file

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Missing project path"
	else:
		project_path=sys.argv[1]
		if len(sys.argv) == 3:
			graph_name=sys.argv[2]
		graph_data=generate_diagrams()
		generate_graph(graph_data)

