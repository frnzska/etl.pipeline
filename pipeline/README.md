####Description

ETL pipeline handling events from stripe webhooks.

####Requirements
- Python path needs to be set to <b>etl.pipeline/pipeline</b>
- AWS credentials configured


####Structure

The pipeline source code consits of the following main components:
1. The source code of the lambda functions and -if needed- a requirements.txt 
 in <b>lambda_functions/xyz_lambda</b>. A zipped version for each function
 and dependencies is provided in <b>lambda_functions/zipped_lambdas</b>. 

2. The code to create infrastructure resources (apigateway, lambdas and statemachine) 
with cloudformation can be found in the folder <b>cfn_stack_builder</b>.

3. An entry script called <i>set_up_pipeline.py</i> to create/delete all resources. 

4. A configuration file config.yml where the resource properties are set.


####Set it up

#####1. Adjust config.yml
Substitude the entrys in the config file with your settings. 
Everything marked with <i># replace ..</i> should be adjusted.

#####2. Deploy lambda zips to s3
In order to create a lambda function with cloudformation the 
lambda function source code and its dependencies should be 
zipped and uploaded to s3. You can use the provided zip files by uncommenting 
Step 1 and 
calling deploy_zipped_lambdas_to_s3() in the set_up_pipeline.py script.
It uploads the zips to the bucket you set in the config.yml.

A second option is to use Travis and Github for zipping and deployment, 
a travis.yml and a bash script in the .travis folder are provided in the parent directory. 

#####3. Create/Delete pipeline resources
To build the resource stack, make sure step 2 has finished and the
 zipped lambdas are on s3. Uncomment Step 2 in the set_up_pipeline.py script
 and call <b>create_pipeline()</b>.
 
Turn down the resources by calling <b>destroy_all()</b>

####Tests
Create and activate conda environment
<pre>
conda env create -f environment.yml -n my_env
source activate my_env
</pre>

and run tests with
<pre>
pytest
</pre>