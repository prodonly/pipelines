# Copyright 2023 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from kfp import dsl


@dsl.component
def flip_coin() -> str:
    import random
    return 'heads' if random.randint(0, 1) == 0 else 'tails'


@dsl.component
def print_and_return(text: str) -> str:
    print(text)
    return text


@dsl.pipeline
def flip_coin_pipeline() -> str:
    flip_coin_task = flip_coin()

    # ONE DAG
    with dsl.If(flip_coin_task.output == 'heads'):
        print_task_1 = print_and_return(text='Got heads!')
    # with dsl.Elif():
    with dsl.Else():
        # For loop
        print_task_2 = print_and_return(text='Got tails!')
    # to output from this dag --> It's a container of pipeline channels
    # ONE DAG

    x = dsl.OneOf(print_task_1.output, print_task_2.output)

    # scope limitation options (not exclusive):
    ## 1 not permitting composing collected into oneof + vice versa
    ## 2 can dsl.OneOf only be outputted from a pipeline, rather than consumed by a task? -- probably cannot do this...
    ## 3 follows from #2... when If, Elif, and Else are used, they have to be at the top level of the DAG

    # TODO(cjmccarthy): discuss with AutoML team

    # as an input: it represents a PipelineChannel
    print_and_return(text=x)
    return x


if __name__ == '__main__':
    from kfp import compiler
    compiler.Compiler().compile(
        pipeline_func=flip_coin_pipeline,
        package_path=__file__.replace('.py', '.yaml'))

if __name__ == '__main__':
    import datetime
    import warnings
    import webbrowser

    from google.cloud import aiplatform
    from kfp import compiler

    warnings.filterwarnings('ignore')
    ir_file = __file__.replace('.py', '.yaml')
    compiler.Compiler().compile(
        pipeline_func=flip_coin_pipeline, package_path=ir_file)
    pipeline_name = __file__.split('/')[-1].replace('_', '-').replace('.py', '')
    display_name = datetime.datetime.now().strftime('%m-%d-%Y-%H-%M-%S')
    job_id = f'{pipeline_name}-{display_name}'
    aiplatform.PipelineJob(
        template_path=ir_file,
        pipeline_root='gs://cjmccarthy-kfp-default-bucket',
        display_name=pipeline_name,
        job_id=job_id).submit()
    url = f'https://console.cloud.google.com/vertex-ai/locations/us-central1/pipelines/runs/{pipeline_name}-{display_name}?project=271009669852'
    webbrowser.open_new_tab(url)