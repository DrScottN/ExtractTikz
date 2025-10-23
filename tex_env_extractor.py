import argparse #for parser cli
import subprocess #to compile standalone files.
import re #for removing comments
import shlex #for formatting shell commands

#create parser for cli
parser = argparse.ArgumentParser(description='Extracts tex environments from a tex file into a standalone template, and creates a new .tex file that points to the seperated environments.')
parser.add_argument("input_filename", help="The .tex file that you wish to remove environments from.")#, epilog="input_filename will not be changed by this program.")
parser.add_argument("--output", help="The .tex file that the result should write to. Defaults to input_filename[:-4] + `_extracted.tex`")
parser.add_argument("--standalone_template", help=r"The .tex file that you wish the environments to use as a template. Should contain a `\envhere` somewhere inside.", default="standalone_template.tex")#, epilog="standalone_template will not be changed by this program.", type=str)
parser.add_argument("--environments", help="any number of latex environment names which should be extracted from input_filename.", default=["tikzpicture"], nargs='*')
parser.add_argument("--tex_command", help="command used for building standalone file (such as 'pdflatex'). Will not compile the images for you if omitted.", default=None, type=str)
parser.add_argument("--tex_args", help="any flags (such as '-shell-escape') for the tex_command.", default=[], nargs='*')
parser.add_argument("--extracted_path", help="path to save new standalone files to. Defaults to current directory, files will have the prefix extracted_.", default="extracted_")

#helper functions

def insert_env_in_file(file_lines, env, replace_string):
    """Replaces each instance of replace_string in the list of strings file_lines with the list of strings env."""
    output_lines = []
    for line in file_lines:
        if replace_string in line:
            output_lines.append(line[:line.index(replace_string)])
            output_lines += env
            output_lines.append(line[line.index(replace_string)+len(replace_string):])
        else:
            output_lines.append(line)
    return output_lines


def create_standalone(env_lines, standalone_file, output_file):
    """Place the given latex lines into a given standalone_file, and save it to output_file."""
    standalone_lines = list(standalone_file)
    output_lines=insert_env_in_file(standalone_lines, env_lines, replace_string=r"\envhere") #Change the 'envhere' on this line to change the template placeholder command '\envhere'.
    output_file.writelines(output_lines)
    return

def environment_standalone_path(extracted_path, env_number, env_name, env_lines, extension=".tex"):
    """Create path for a given extracted environment."""
    return extracted_path+env_name+"_"+str(env_number)+extension #simplest version will not be in a directory, less permissions. Could incorporate lines properties.

def compile_standalone(tex_command, filename, tex_arguments=[]):
    """Run tex_command on filename."""
    try:
        package = [tex_command]
        for t in tex_arguments:
            package.append(t)
        package.append(filename)
        print("Running the command: ", package)
        subprocess.run(package, check=True) #, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        print(error)

def remove_comments(latex_string):
    """Remove commented out suffix from string."""
    regex_for_unescaped_comment = r"[^\\]%" #matches unescaped %'s
    comment_match = re.search(regex_for_unescaped_comment, latex_string)
    if comment_match:
        return latex_string[:comment_match.start()]
    else:
        return latex_string

def replace_environments(latex_file, environments, extracted_path):
    regex_for_begin_env = r"\\begin\{(" + r"|".join([re.escape(env) for env in environments]) + r")\}"
    latex_lines = list(latex_file)
    line_count = len(latex_lines)
    assert line_count > 0, "Empty input file."
    #initialize loop
    extracted_envs = []
    output_lines =[]
    in_env = False #state; what environment (of our list) are we currently in?
    line = latex_lines[0]
    commentless_line = remove_comments(line)
    i=0 #state; what line number are we reading
    while True:
        if in_env:
            regex_for_end_env = r"\\end\{" + re.escape(in_env) + r"\}"
            match = re.search(regex_for_end_env, commentless_line)
            if match: #end of environment found.
                inside_line=line[:match.end()]
                env_lines.append(inside_line)
                output_lines.append(r"\includegraphics{" + 
                    environment_standalone_path(extracted_path, len(extracted_envs), in_env, env_lines, extension="")+ "}")
                extracted_envs.append(env_lines)

                #haven't parsed the rest of this line; restart loop with it.
                line = line[match.end():]
                commentless_line = remove_comments(line)
                in_env=False
                continue
            env_lines.append(line)
        else:
            match = re.search(regex_for_begin_env, commentless_line) #finds the first substring that matches
            if match: #beginning of environment found.
                #strip prefix
                prefix = line[:match.start()]
                output_lines.append(prefix)
                line = line[match.start():]
                commentless_line = commentless_line[match.start():]
                #change loop mode
                in_env=match.group(1) #store which environment we're in
                env_lines=[]
                continue
            output_lines.append(line) #otherwise write to output
        i+=1
        if i==line_count:
            break
        line = latex_lines[i]
        commentless_line = remove_comments(line)
    return extracted_envs, output_lines

def main(input_filename, output_filename, standalone_template_filename, environments, tex_compiler_command, tex_compiler_args, extracted_path):
    with open(input_filename, 'r') as input_file:
        extracted_envs, output_lines = replace_environments(input_file, environments, extracted_path)

    with open(output_filename, 'w') as output_file:
        output_file.writelines(output_lines)
    print("created new file " + str(output_filename) + " with includegraphics.")

    for env_number in range(len(extracted_envs)):
        env_lines = extracted_envs[env_number]
        env_name = env_lines[0][7:]
        env_name = env_name[:env_name.index("}")] #extract contents of \begin{*}
        with open(environment_standalone_path(extracted_path, env_number, env_name, env_lines), 'w') as out_env_file, open(standalone_template_filename, 'r') as standalone_file:
            create_standalone(env_lines, standalone_file, out_env_file)
    print("created standalone files for " + str(len(extracted_envs)) + " environments.")
    
    if not tex_compiler_command:
        print("no tex compiler provided. Standalone files must be compiled separately.")
    else:
        for env_number in range(len(extracted_envs)):
            env_lines = extracted_envs[env_number]
            env_name = env_lines[0][7:]
            env_name = env_name[:env_name.index("}")] #extract contents of \begin{*}
            compile_standalone(tex_compiler_command, environment_standalone_path(extracted_path, env_number, env_name, env_lines), tex_arguments=tex_compiler_args)
        print("compiled the standalone environments.")
    
if __name__=='__main__':
    args = parser.parse_args()
    if not args.output:
        output_filename = args.input_filename[:-4] + "_extracted.tex"
    else:
        output_filename = args.output
    if args.tex_command:
        sample_env = args.environments[0] if args.environments else "environment"
        sample_target = f"{args.extracted_path}{sample_env}_0.tex"
        sample_command = [args.tex_command, *args.tex_args, sample_target]
        command_preview = " ".join(shlex.quote(token) for token in sample_command)
        confirmation = input(f"This will run `{command_preview}` for each extracted environment. Continue? [y/N]: ").strip().lower()
        if confirmation not in ("y", "yes"):
            print("Compilation step skipped at user request.")
            args.tex_command = None
    main(args.input_filename, output_filename, args.standalone_template, args.environments, args.tex_command, args.tex_args, args.extracted_path)
