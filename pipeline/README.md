### Description

ETL pipeline handling events from stripe webhooks.

### Requirements
- Python path needs to be set to <b>etl.pipeline/pipeline</b>, e.g.:
 <pre>
cd etl.pipeline
export PYTHONPATH=$PYTHONPATH:$PWD/pipeline
</pre>
- AWS credentials configured, profile set and added as environment variable , e.g.:
<pre>
export AWS_DEFATULT_REGION=eu-west-1
export AWS_PROFILE=profilename
</pre>


### Structure

The pipeline source code consits of the following main components:
1. The source code of the lambda functions and -if needed- a requirements.txt 
 in <b>lambda_functions/xyz_lambda</b>. A zipped version for each function
 and dependencies is provided in <b>lambda_functions/zipped_lambdas</b>. 

2. The code to create infrastructure resources (apigateway, lambdas and statemachine) 
with cloudformation can be found in the folder <b>cfn_stack_builder</b>.

3. An entry script called <i>set_up_pipeline.py</i> to create/delete all resources. 

4. A configuration file config.yml where the resource properties are set.


### Set it up

#### 1. Activate environment

<pre>
conda env create -f environment.yml -n my_env
source activate my_env
</pre>

#### 2. Adjust config.yml
Substitude the entrys in the config file with your settings. 
Everything marked with <i># replace ..</i> should be adjusted.

#### 3. Deploy lambda zips to s3
In order to create a lambda function with cloudformation the 
lambda function source code and its dependencies should be 
zipped and uploaded to s3. You can use the provided zip files by
calling deploy_zipped_lambdas_to_s3() in the set_up_pipeline.py script.
For example uncomment Step 1 and run
<pre>
python pipeline/set_up_pipeline.py
</pre>

It uploads the zips to the bucket you set in the config.yml.

A second option is to use Travis and Github for zipping and deployment, 
a travis.yml and a bash script in the .travis folder are provided in the parent directory. 

#### 4. Create/Delete pipeline resources
To build the resource stack, uncomment Step 2 in the set_up_pipeline.py script
 and call <b>create_pipeline()</b>.
 
Turn down the resources by calling <b>destroy_all()</b>

### Tests
Activate conda environment and run tests with
<pre>
source activate my_env
pytest
</pre>

### Assumptions I made
- There are different event types coming from stripes webhooks but all have at least the properties
<b>id, type, </b> and a <b>data.object</b> with a <b>source</b> field. 
- For the rds lambda function I assume there are staging tables where the events are stored 
as a starting point for dimensional modelling

### What I would like to improve but ran out of time
- Add api gateway model for events validation
- encrypt/decrypt rds information
- integration tests
