# Copyright 2021 The Kubeflow Authors
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
"""Importer-based component."""

from typing import List

from kfp.components import base_component
from kfp.components import structures


class ImporterComponent(base_component.BaseComponent):
    """Component defined via dsl.importer."""

    def __init__(
        self,
        component_spec: structures.ComponentSpec,
    ):
        super().__init__(component_spec=component_spec)

    def execute(self, **kwargs):
        raise NotImplementedError

    @property
    def required_inputs(self) -> List[str]:
        return []
