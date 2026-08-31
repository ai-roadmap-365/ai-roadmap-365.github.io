"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, List, Optional, Callable

class MCPResourcePromptEngine:

    def __init__(self, server_name: str='doc-server'):
        self.server_name = server_name
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.prompts: Dict[str, Dict[str, Any]] = {}

    def register_resource(self, uri: str, name: str, mime_type: str, reader_fn: Callable[[], str]):
        raise NotImplementedError('TASK 1: implement register_resource.')

    def register_prompt(self, name: str, description: str, arguments: List[Dict[str, Any]], template_fn: Callable[..., List[Dict[str, Any]]]):
        raise NotImplementedError('TASK 2: implement register_prompt.')

    def handle_request(self, method: str, params: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement handle_request.')
if __name__ == '__main__':
    engine = MCPResourcePromptEngine('doc-server')
    engine.register_resource('memo://active', 'Active Note', 'text/plain', lambda: 'Deploying model v2')
    engine.register_prompt('summarize', 'Summarize a document', [{'name': 'doc', 'required': True}], lambda doc: [{'role': 'user', 'content': {'type': 'text', 'text': f'Summarize: {doc}'}}])
    print('Resources:', engine.handle_request('resources/list'))
    print('Prompts:', engine.handle_request('prompts/list'))
