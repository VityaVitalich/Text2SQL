import importlib
import yaml
import openai
from ratelimit import limits, sleep_and_retry


class QueryInterface:

    def __init__(self):
        '''
        Initialization of model and all arguments
        '''
        pass

    def query(self):
        '''
        query model with a question. extra arguments needed when using specific models
        '''
        pass

    def _init_model(self):
        '''
        Model initialization, with a path of configs
        '''
    def _init_prompter(self):
        '''
        Initialization of Prompt Changer class from config
        '''

class HF_LLMQuery(QueryInterface):

    def __init__(self, model_config_path, prompt_config_path, *args, **kwargs):
        self.model, self.tokenizer, self.generation_args = self._init_model(model_config_path)
        self.prompt_style = self._init_prompter(prompt_config_path)
        
    def query(self, question, **kwargs):

        prompt = self.prompt_style(question, **kwargs)
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        
        output = self.model.generate(input_ids=input_ids, **self.generation_args)
        out_text = self.tokenizer.decode(output[0], skip_special_tokens=True)

        return out_text

    def _init_model(self, model_config_path):

        with open(f'{model_config_path}','r') as f:
            configs = yaml.safe_load(f)

        module = importlib.import_module('transformers')

        TokenizerClass = module.__getattr__(configs['TokenizerClass'])
        ModelClass = module.__getattr__(configs['ModelClass'])

        tokenizer = TokenizerClass.from_pretrained(**configs['tokenizer'])
        model = ModelClass.from_pretrained(**configs['model'])

        return model, tokenizer, configs['generation_args']

    def _init_prompter(self, prompt_config_path):

        with open(f'{prompt_config_path}','r') as f:
            configs = yaml.safe_load(f)

        module = importlib.import_module('prompting.hf_prompt_schemas')

        prompt_class = getattr(module, configs['PromptClass'])

        return prompt_class(**configs['prompt_configs'])
    

class OpenAI_LLMQuery(QueryInterface):

    def __init__(self, model_config_path, prompt_config_path, *args, **kwargs):
        self.model, self.generation_args = self._init_model(model_config_path)
        self.prompt_style = self._init_prompter(prompt_config_path)


    def query(self, question, **kwargs):

        prompt = self.prompt_style(question, **kwargs)
        out_text = self.get_answer(prompt)

        return out_text

    def _init_model(self, model_config_path):

        with open(f'{model_config_path}','r') as f:
            configs = yaml.safe_load(f)

        openai.api_key = configs['token']


        return openai.ChatCompletion, configs['generation_args']

    def _init_prompter(self, prompt_config_path):

        with open(f'{prompt_config_path}','r') as f:
            configs = yaml.safe_load(f)

        module = importlib.import_module('prompting.openai_prompt_schemas')

        prompt_class = getattr(module, configs['PromptClass'])

        return prompt_class(**configs['prompt_configs'])

    @sleep_and_retry
    @limits(calls=3, period=62)
    def get_answer(self, prompt: str) -> str:
        completion = self.model.create(
            messages = prompt,
            **self.generation_args
        )
        return str(completion["choices"][0]["message"]["content"])


