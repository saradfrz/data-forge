FROM jupyter/pyspark-notebook:x86_64-spark-3.5.0

# Create a virtual environment and install dependencies
RUN python -m venv /home/jovyan/venv && \
    /home/jovyan/venv/bin/pip install --no-cache-dir pyspark==3.5.5 python-dotenv ipykernel

# Install the virtual environment as a Jupyter kernel
RUN /home/jovyan/venv/bin/python -m ipykernel install --user --name=myenv --display-name "Python (myenv)"

# Set the default kernel
RUN echo "c.NotebookApp.kernel_name = 'myenv'" >> /home/jovyan/.jupyter/jupyter_notebook_config.py

# Preserve the default command
CMD ["start-notebook.sh", "--NotebookApp.token=''"]