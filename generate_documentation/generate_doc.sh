echo "Exporting BASE_DIR..."
BASE_DIR=$(dirname "$(pwd)")/MS-CHARAC-BACK
echo "BASE_DIR: $BASE_DIR"
export BASE_DIR

echo "Installing Sphinx and sphinx-rtd-theme..."
sudo apt-get install -y python3-sphinx
sudo apt-get install -y python3-sphinx-rtd-theme 

echo "Installing LaTeX for PDF documentation generation..."
sudo apt-get install -y texlive-full
sudo apt-get install -y texlive latexmk

echo "Building the python library..."
echo "Going to the root directory of the project..."
echo $(pwd)
echo "Installing the python library..."
pip install -e .
cd ${BASE_DIR}

echo "Creating the docs directory..."
cd MS-CHARAC-BACK
sudo rm -rf docs
mkdir docs
cd docs
sphinx-quickstart -q \
  -p "MS CHARAC DOCUMENTATION" \
  -a "Khadija Yasmine Mzabi" \
  -v 1.0 \
  --dot=_ \
  --extensions=sphinx.ext.autodoc,sphinx.ext.todo,sphinx.ext.viewcode \
  --makefile \
  --no-use-make-mode \
  

cd ${BASE_DIR}
echo "Executing sphinx-apidoc and make html in the directory: ${BASE_DIR}/MS-CHARAC-BACK..."
sphinx-apidoc -o docs .
cd ${BASE_DIR}

python3 MS-CHARAC-BACK/generate_documentation/adjust_paths_rst.py

echo "Modifying the conf.py file..."  
cd ${BASE_DIR}/MS-CHARAC-BACK/generate_documentation
sudo -E python3 modify_conf.py

cd ${BASE_DIR}/docs
make html

make latexpdf
echo "PDF documentation is ready at ${BASE_DIR}/docs/_build/latex/MSCHARAC-BACKEND.pdf"
echo "Documentation is ready at ${BASE_DIR}/docs/_build/html/index.html"
