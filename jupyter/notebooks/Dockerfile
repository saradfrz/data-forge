FROM jupyter/pyspark-notebook:latest

# Install python-dotenv during the image build
RUN pip install python-dotenv
RUN pip install pyspark==3.5.5

# The default CMD for starting the notebook is preserved
CMD ["start-notebook.sh", "--NotebookApp.token=''"]
