# Copyright 2022 The Kubeflow Authors
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
import sys
import tempfile


def create_temporary_non_kfp_artifact_package(
        temp_dir: tempfile.TemporaryDirectory) -> None:
    import inspect
    import os
    import textwrap

    class ThirdPartyModel:
        schema_title = 'third_party.ThirdPartyModel'
        schema_version = '0.0.0'

        def __init__(self, name: str, uri: str, metadata: dict) -> None:
            self.name = name
            self.uri = uri
            self.metadata = metadata

        @property
        def path(self) -> str:
            return self.uri.replace('gs://', '/')

    class_source = textwrap.dedent(inspect.getsource(ThirdPartyModel))

    with open(os.path.join(temp_dir.name, 'dummy_third_party_package.py'),
              'w') as f:
        f.write(class_source)


# remove try finally when a third-party package adds pre-registered custom artifact types that we can use for testing
try:
    temp_dir = tempfile.TemporaryDirectory()
    sys.path.append(temp_dir.name)
    create_temporary_non_kfp_artifact_package(temp_dir)

    import dummy_third_party_package
    from dummy_third_party_package import ThirdPartyModel
    from kfp import compiler
    from kfp import dsl
    from kfp.dsl import Input
    from kfp.dsl import Output

    PACKAGES_TO_INSTALL = ['dummy-third-party-package']

    @dsl.component(packages_to_install=PACKAGES_TO_INSTALL)
    def model_producer(
            model: Output[dummy_third_party_package.ThirdPartyModel]):

        assert isinstance(
            model, dummy_third_party_package.ThirdPartyModel), type(model)
        with open(model.path, 'w') as f:
            f.write('my model')

    @dsl.component(packages_to_install=PACKAGES_TO_INSTALL)
    def model_consumer(model: Input[ThirdPartyModel]):
        print('artifact.type: ', type(model))
        print('artifact.name: ', model.name)
        print('artifact.uri: ', model.uri)
        print('artifact.metadata: ', model.metadata)

    @dsl.pipeline(name='pipeline-with-vertex-types')
    def my_pipeline():
        producer_task = model_producer()
        model_consumer(model=producer_task.outputs['model'])

    if __name__ == '__main__':
        ir_file = __file__.replace('.py', '.yaml')
        compiler.Compiler().compile(
            pipeline_func=my_pipeline, package_path=ir_file)
finally:
    sys.path.pop()
    temp_dir.cleanup()