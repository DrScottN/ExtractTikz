# ExtractTikz
Scripts to make latex documents more accessible, by separately compiling tikz environments as images.
These scripts will automate extracting environments from a tex file, compiling them seperately, and including them in the original file automatically.

The primary use case is for removing tikzpicture and picture environments, which do not compile to HTML on the arXiv.

# Notes on creating image files
Compiling standalone to an image file: this is not always trivial. Include graphics will include pdfs, but by default these are recompiled instead of included as images.
Guides:
[standalone->svg on tex exchange](https://tex.stackexchange.com/questions/51757/how-can-i-use-tikz-to-make-standalone-svg-graphics)
[standalone->png on stack exchange](https://stackoverflow.com/questions/77614081/how-i-can-produce-a-png-from-a-tizk-tex-file-with-class-standalone)

# Example usage
```bash
python tex_env_extractor.py main.tex
```

This will create/overwrite one file titled `extracted_tikzpicture_##.tex` for each tikzpicture environment in `main.tex`, which will be a copy of `standalone_template.tex` with the first `\envhere` command replaced by the complete tikzpicture environment. 
It will also create the file `main_extracted.tex`, which is a copy of `main.tex` with every tikzpicture environment replaced by `\includegraphics{extracted_tikzpicture_##}` for the appropriate ##. 
You can now seperately compile each `extracted_tikzpicture_##.tex` with your preferred tex compiler, and then `main_extracted.tex`.

If you used the example `standalone_template.tex`, then compiling these files will result in svg files, and the resulting `main_extracted.tex` will have no dependancies on tikz. In particular, it may now compile to (or compile to better looking) HTML, for example on arXiv.
When uploading to arXiv, you need only include `main_extracted.tex` and the final svg files (though it is kind to include the associated `.tex` files, so others may see how your images were created).

# Advanced features
Without doing anything with python or the command line, you have some flexability. You may edit the `standalone_template.tex` in the repository to include useful packages, standardize formatting, insert a uniform watermark, etc.

The script accepts several additional inputs, which you can also view by running python tex_env_extractor.py -h.

--output : the name of the new tex file after all the environments are replaced by includegraphics (main_extracted.tex in the example above).

--standalone_template : the name of a tex file that includes the line '\envhere' somewhere, which is used to make all the extracted files (standalone_template.tex in the example above).

--environments : a sequence of tex environments you would like to extract and replace. For example, 
`python main.tex --environments picture tikzpicture tikzcd`

will create a standalone file for each picture, tikzpicture, and tikzcd block (the created files will indicate which environment is in each in their names, for example you could see some extracted_picture_##.tex ).

--tex_command : you can provide the string for your latex compiler, and the program will automatically call it on each of the extracted_tikzpicture_##.tex files. Specifically, it will try to run 'tex_command extracted_environment_##.tex' (the filename will match the created files for the environment). Note this will not be used on the final new tex file (eg main_extracted.tex).

--extracted_path : For large projects, there may be many extracted environments. You can change where they are located, and what prefix is used for the filenames, by setting this value. By default, it uses "extracted_". Setting it to "figures/extracted_" will create all the standalone files in the figures folder. Note that you may need to create the figures folder, or else the program will fail.
