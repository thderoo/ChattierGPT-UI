# ChattierGPT
A Simple and Powerful UI for the ChatGPT API.

ChattierGPT is a Python application for local use (colab version coming soon) that allows to communicate with the OpenAI ChatGPT API (gpt-3.5-turbo only for now).

ChattierGPT has a simple and complete interface, offering a compromise between what the official OpenAI chat interface allows and the advanced options of the developer API.

This tool is still in beta, bug reports and improvements are welcome!

## How to use

### Windows

- Unzip the file
- Run ChattierGPT
- A console window should open, wait for the application to launch in your browser, or go to the url displayed on the console.

The first launch requires an internet connection and may take a few minutes, please wait while python installs the necessary packages.

### From a Python environment

Installation of the required packages:

```
pip install -r requiremets.txt
```

Launching the UI:

```
python -m streamlit run src/main.py
```

## Features
Features marked with "💬" are available in chat.openai.com, those with "🤖" are platform.openai.com features, "🆕" are new features.

### Available features

- API pricing 🤖
- Multiple chats 💬
- Custom system prompts 🤖
- Loading system prompts from txt files 🆕
- Advanced model parameters (Temperature, top p, max length, penalties) 🤖
- Global context length limiter 🆕
- Markdown support for user messages 🆕
- LaTeX formula support 🆕
- HTML support 🆕
- Branching conversations 💬
- ChatGPT response editing 🤖
- Deleting messages 🤖
- Display of token count of messages and of context length 🆕

### Planed features

- Automatic generation of conversation titles with ChatGPT (togglable option)
- Colab compatibility
- Migration from Streamlit to a better framework
- More customization, including custom add-on support
- Feel free to suggest other additions!

## About the API

This tool is only intended to interact with the official OpenAI API, I do not plan to make it compatible with chat.openai.com in the near future.

To get access to the API, you need to create an account on platform.openai.com and create an API key, you can find a tutorial here: https://elephas.app/blog/how-to-create-openai-api-keys-cl5c4f21d281431po7k8fgyol0

The access to the OpenAI API is not free, the prices are available on the following page (for the moment ChattierGPT only supports gpt-3.5-turbo): https://openai.com/pricing

## Disclaimer

ChattierGPT is a tool to facilitate access to the ChatGPT API, I therefore cannot be held responsible for the use you will make of it.

Please use this tool responsibly and in accordance with the OpenAI terms of use available at: https://openai.com/policies/terms-of-use
