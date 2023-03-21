from datetime import datetime
import json

import openai as oa
import tiktoken as tt

class Chat:
    def __init__(self, created=None, model='gpt-3.5-turbo', context=None, temperature=0.7, top_p=1.0, max_tokens=512,
                 max_context_tokens=4096, frequency_penalty=0.0, presence_penalty=0.0):
        self.created = int(datetime.now().timestamp()) if created is None else created
        self.model = model
        self.encoder = tt.encoding_for_model(model)
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.max_context_tokens = max_context_tokens - max_tokens
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

        self.messages = {
            'role': 'system',
            'content': "",
            'next': [],
            'selected': None
        }

        if context is not None:
            self.messages['content'] = context

        self.messages['context_tokens'] = 0
        self.count_tokens(self.messages)

    def save(self, filename=None, folder='chats/'):
        if filename is None:
            filename = '%s.json' % self.created

        with open(folder + filename, 'w') as f:
            json.dump(self, f, default=lambda o: {k: v for k, v in o.__dict__.items() if k not in ('encoder', )},
                      sort_keys=True)

    @staticmethod
    def load(filename, folder='chats/'):
        with open(folder + filename, 'r') as f:
            chat = Chat()
            chat.__dict__ = json.load(f)

        chat.encoder = tt.encoding_for_model(chat.model)

        return chat

    def get_selected_path(self, length=None):
        path = [self.messages]

        while path[-1]['selected'] is not None and (length is None or len(path) < length):
            path.append(path[-1]['next'][path[-1]['selected']])

        return path

    def add_message(self, content, index=None, role='user'):
        current_tree = self.messages

        if index is None:
            while current_tree['selected'] is not None:
                current_tree = current_tree['next'][current_tree['selected']]
        else:
            for i in range(index - 1):
                current_tree = current_tree['next'][current_tree['selected']]

        current_tree['next'].append({'role': role,
                                     'content': content,
                                     'tokens': len(self.encoder.encode(content)) + 5,
                                     'context_tokens': current_tree['context_tokens'] + current_tree['tokens'],
                                     'next': [],
                                     'selected': None})
        current_tree['selected'] = len(current_tree['next']) - 1

    def delete_message(self, index):
        current_tree = self.messages

        for i in range(index - 1):
            current_tree = current_tree['next'][current_tree['selected']]

        del current_tree['next'][current_tree['selected']]
        current_tree['selected'] -= 1
        current_tree['selected'] = (None if len(current_tree['next']) == 0 else 0)\
            if current_tree['selected'] == -1 else current_tree['selected']

    def count_tokens(self, tree):
        tree['tokens'] = len(self.encoder.encode(tree['content'])) + 5

        for n in tree['next']:
            n['context_tokens'] = tree['context_tokens'] + tree['tokens']
            self.count_tokens(n)

    def generate(self, index=None):
        if index is None:
            path = self.get_selected_path()
        else:
            path = self.get_selected_path(length=index)

        i = 1
        token_count = self.messages['tokens']
        for i, m in list(enumerate(path))[1:][::-1]:
            if token_count + m['tokens'] <= self.max_context_tokens:
                token_count += m['tokens']
            else:
                i += 1
                break

        self.add_message(self.chat_completion([self.messages] + path[i:]), index=index, role='assistant')

    def chat_completion(self, path):
        conversation = {
            'model': self.model,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_tokens,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'messages': [{'role': m['role'], 'content': m['content']} for m in path]
        }

        response = oa.ChatCompletion.create(**conversation)
        response['choices'][0]['message']['content'] = response['choices'][0]['message']['content'].strip()

        return response['choices'][0]['message']['content']
