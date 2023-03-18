import json
import os

from datetime import datetime

from chat import Chat

import streamlit as st
import openai as oa


def save_chat_names():
    with open('chats/chat_names.json', 'w') as f:
        json.dump(st.session_state['chat_names'], f)


def load_chat_names():
    with open('chats/chat_names.json', 'r') as f:
        st.session_state['chat_names'] = json.load(f)


st.set_page_config(layout='wide')

if 'main' not in st.session_state:
    with open('main.json', 'r') as f:
        st.session_state['main'] = json.load(f)

    if 'api_key' in st.session_state['main']:
        oa.api_key = st.session_state['main']['api_key']

if 'tooltips' not in st.session_state:
    with open('tooltips.json', 'r') as f:
        st.session_state['tooltips'] = json.load(f)

tooltips = st.session_state['tooltips']

st.session_state['chats'] = \
    sorted([{'filename': f, 'modified': os.path.getmtime('chats/%s' % f)}
            for f in os.listdir('chats') if f != 'chat_names.json'],
           key=lambda o: o['modified'], reverse=True)

if 'chat_names' not in st.session_state:
    load_chat_names()

if set(c['filename'] for c in st.session_state['chats']) != set(st.session_state['chat_names'].keys()):
    for c in st.session_state['chats']:
        if c['filename'] not in st.session_state['chat_names']:
            st.session_state['chat_names'][c['filename']] =\
                datetime.fromtimestamp(int(c['filename'].split('.')[0])).strftime('%Y-%m-%d %H:%M:%S')

    for k in list(st.session_state['chat_names'].keys()):
        if k not in [c['filename'] for c in st.session_state['chats']]:
            del st.session_state['chat_names'][k]

    save_chat_names()
    st.experimental_rerun()

chat_names = st.session_state['chat_names']

if 'current_chat' not in st.session_state:
    if len(st.session_state['chats']) == 0:
        st.session_state['current_chat'] = Chat(context=open('prompts/default_en.txt', 'r').read())
        st.session_state['current_chat'].save()
        st.experimental_rerun()
    else:
        st.session_state['current_chat'] = Chat.load(st.session_state['chats'][0]['filename'])

current_chat = st.session_state['current_chat']

#### SIDEBAR
with st.sidebar:
    st.title('ChattierGPT')

    with st.expander('Global parameters', expanded=False):
        def api_key_changed():
            st.session_state['main']['api_key'] = st.session_state['api_key_input']

            with open('main.json', 'w') as f:
                json.dump(st.session_state['main'], f)

        st.text_input('API key',
                      value=st.session_state['main']['api_key'] if 'api_key' in st.session_state['main'] else '',
                      type='password', on_change=api_key_changed, key='api_key_input',
                      help=tooltips['api_key'])

    if st.button('New chat', use_container_width=True):
        current_chat.save()
        st.session_state['current_chat'] = Chat(context=open('prompts/default_en.txt', 'r').read())
        st.session_state['current_chat'].save()
        st.experimental_rerun()

    for c in st.session_state['chats']:
        created = int(c['filename'].split('.')[0])
        with st.form('chat_%d' % created):
            if 'renaming' not in st.session_state or st.session_state['renaming'] != c['filename']:
                st.subheader(chat_names[c['filename']])
            else:
                chat_name = st.text_input('Chat name', value=chat_names[c['filename']],
                                          label_visibility='collapsed')

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.form_submit_button('Load', use_container_width=True):
                    current_chat.save()
                    st.session_state['current_chat'] = Chat.load(c['filename'])
                    st.experimental_rerun()

            with col2:
                if st.form_submit_button('Delete', use_container_width=True):
                    os.remove('chats/%s' % c['filename'])

                    del chat_names[c['filename']]
                    save_chat_names()

                    if created == current_chat.created:
                        del st.session_state['current_chat']
                    st.experimental_rerun()

            with col3:
                if st.form_submit_button('Rename', use_container_width=True):
                    if 'renaming' not in st.session_state or st.session_state['renaming'] != c['filename']:
                        st.session_state['renaming'] = c['filename']
                    else:
                        st.session_state['renaming'] = None
                        chat_name = chat_name.strip()
                        if len(chat_name) > 0:
                            chat_names[c['filename']] = chat_name
                            save_chat_names()

                    st.experimental_rerun()


col1, col2 = st.columns([3, 1])

#### PARAMETERS
with st.expander('Parameters'):
    system_tokens = current_chat.messages['tokens']
    system_prompt = st.text_area('System prompt (tokens: %d)' % system_tokens, value=current_chat.messages['content'],
                                 help=st.session_state['tooltips']['system_prompt'])
    current_chat.messages['content'] = system_prompt
    current_chat.count_tokens(current_chat.messages)

    col1, col2, col3, _, col4 = st.columns([1, 1, 1, 3, 1])

    with col1:
        current_chat.temperature = st.slider('Temperature', min_value=0.0, max_value=1.0,
                                             value=current_chat.temperature,
                                             help=tooltips['temperature'])
        current_chat.top_p = st.slider('Top P', min_value=0.0, max_value=1.0, value=current_chat.top_p,
                                       help=tooltips['top_p'])

    with col2:
        current_chat.max_tokens = st.slider('Maximum length', min_value=1, max_value=2048,
                                            value=current_chat.max_tokens, help=tooltips['max_tokens'])

        current_chat.max_context_tokens = st.slider('Maximum context length', min_value=system_tokens,
                                                    max_value=4096 - current_chat.max_tokens,
                                                    value=max(system_tokens, current_chat.max_context_tokens),
                                                    help=tooltips['max_context_tokens'])

    with col3:
        current_chat.frequency_penalty = st.slider('Frequency penalty', min_value=-2.0, max_value=2.0,
                                                   value=current_chat.frequency_penalty,
                                                   help=tooltips['frequency_penalty'])
        current_chat.presence_penalty = st.slider('Presence penalty', min_value=-2.0, max_value=2.0,
                                                  value=current_chat.presence_penalty,
                                                  help=tooltips['presence_penalty'])

    with col4:
        prompts = sorted(os.listdir('prompts'))

        def load_prompt():
            with open('prompts/%s' % st.session_state['prompt_file'], 'r', encoding='utf-8') as f:
                current_chat.messages['content'] = f.read()
                current_chat.count_tokens(current_chat.messages)
                current_chat.save()

        st.selectbox('Load system prompt', prompts, on_change=load_prompt, key='prompt_file', disabled=False)

    if st.button('Save parameters'):
        current_chat.save()

#### PROMPT
with st.form('prompt', clear_on_submit=True):
    prompt = st.text_area('Prompt')

    col1, _ = st.columns([1, 10])

    with col1:
        if st.form_submit_button('Send', use_container_width=True):
            if len(prompt) > 0:
                current_chat.add_message(prompt)

            current_chat.generate()
            current_chat.save()

#### MESSAGES
path = list(enumerate(current_chat.get_selected_path()))
''

for i, m in path[::-1]:
    if m['role'] != 'system':
        container = st.empty()

        if 'editing' in m and m['editing']:
            content = container.text_area('Content', m['content'], label_visibility='collapsed')
        else:
            container.markdown(m['content'].replace('\n\n', '\n').replace('\n', '\n\n'), unsafe_allow_html=True)

        col1, col2, col3, col4, col5, _, col6 = st.columns([1, 1, 1, 1, 2, 3, 1])

        with col1:
            st.selectbox('Role', ['User', 'Assistant'], index=0 if m['role'] == 'user' else 1, key='role_%d' % i,
                         label_visibility='collapsed')

        with col2:
            if st.button('Edit', use_container_width=True, key='edit_%d' % i):
                if 'editing' in m and m['editing']:
                    m['editing'] = False
                    m['content'] = content
                    current_chat.count_tokens(m)
                    current_chat.save()
                else:
                    m['editing'] = True

                st.experimental_rerun()

        with col3:
            if st.button('Regenerate', use_container_width=True, key='regenerate_%d' % i):
                current_chat.generate(i)
                current_chat.save()
                st.experimental_rerun()

        with col4:
            if st.button('Delete', use_container_width=True, key='delete_%d' % i):
                current_chat.delete_message(i)
                current_chat.save()
                st.experimental_rerun()

        with col5:
            st.markdown('Tokens: %d, Context tokens: %d' % (m['tokens'], m['context_tokens']))

        with col6:
            def version_changed(i):
                path[i - 1][1]['selected'] = st.session_state['number_%d' % i]
                current_chat.save()

            versions = len(path[i - 1][1]['next'])
            selected = st.number_input('Version', min_value=0, max_value=versions - 1, value=path[i - 1][1]['selected'],
                                       step=1, label_visibility='collapsed', on_change=version_changed, args=[i],
                                       key='number_%d' % i)

        st.markdown('---')