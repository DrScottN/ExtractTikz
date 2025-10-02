from TexSoup import TexSoup
import argparse #for parser cli
import subprocess #to compile standalone files.

#create parser for cli
parser = argparse.ArgumentParser(description=r'Extracts tex environments from a tex file into a standalone template, and creates a new .tex file that points to the seperated environments.')
parser.add_argument("input_filename", help=r"The .tex file that you wish to remove environments from.")#, epilog="input_filename will not be changed by this program.")
parser.add_argument("--output", help=r"The .tex file that the result should write to. Defaults to input_filename[:-4] + `_extracted.tex`")
parser.add_argument("--standalone_template", help=r"The .tex file that you wish the environments to use as a template. Should contain a `\envhere` somewhere inside.", default="standalone_template.tex")#, epilog="standalone_template will not be changed by this program.", type=str)
parser.add_argument("--environments", help=r"any number of latex environment names which should be extracted from input_filename.", default=["tikzpicture"], nargs='*')
parser.add_argument("--tex_command", help=r"command used for building standalone file. Will not compile if omitted.", default=None, type=str)
parser.add_argument("--extracted_path", help=r"path to save new standalone files to. Defaults to current directory, files will have the prefix extracted_.", default="extracted_")

#helper functions

def create_standalone(env_node, standalone_file, output_file):
    """Place the given latex node into a given standalone_file, and save it to output_file."""
    standalone_soup = TexSoup(standalone_file)
    standalone_soup.envhere.replace_with(env_node) #Change the 'envhere' on this line to change the template placeholder command '\envhere'.
    output_file.write(str(standalone_soup))
    return

def environment_standalone_path(extracted_path, env_number, env_node, extension=".tex"):
    """Create path for a given extracted environment."""
    return extracted_path+str(env_node.name)+"_"+str(env_number)+extension #simplest version will not be in a directory, less permissions. Could incorporate node properties.

def compile_standalone(tex_command, filename):
    """Run tex_command on filename."""
    subprocess.run([tex_command, filename], check=True) #, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    

def main(input_filename, output_filename, standalone_template_filename, environments, tex_compiler_command, extracted_path):
    with open(input_filename) as latex_file:
        soup = TexSoup(latex_file)
        extracted_envs = list(soup.find_all(environments))

    for env_number in range(len(extracted_envs)):
        node = extracted_envs[env_number]
        with open(environment_standalone_path(extracted_path, env_number, node), 'w') as out_env_file, open(standalone_template_filename, 'r') as standalone_file:
            create_standalone(node, standalone_file, out_env_file)
    print("created standalone files for " + str(len(extracted_envs)) + " environments.")
    
    if not tex_compiler_command:
        print("no tex compiler provided. Standalone files ")
    else:
        for env_number in range(len(extracted_envs)):
            compile_standalone(tex_compiler_command, environment_standalone_path(extracted_path, env_number, node))
        print("compiled the standalone environments.")

    for env_number in range(len(extracted_envs)):
        node = extracted_envs[env_number]
        paren = node.parent
        #the following operation updates soup, creating our new output file.
        paren.replace(node, r"\includegraphics{" + environment_standalone_path(extracted_path, env_number, node, extension="")+ "}")
    with open(output_filename, 'w') as output_file:
        output_file.write(str(soup))
    print("created new file " + str(output_filename) + " with generated environments.")
    
if __name__=='__main__':
    args = parser.parse_args()
    if not args.output:
        output_filename = args.input_filename[:-4] + "_extracted.tex"
    else:
        output_filename = args.output
    #todo: if tex_command, prompt user with example command that will be called.
    main(args.input_filename, output_filename, args.standalone_template, args.environments, args.tex_command, args.extracted_path)
