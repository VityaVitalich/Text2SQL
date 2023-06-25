import importlib
import yaml

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

        module = importlib.import_module('prompting.prompt_schemas')

        prompt_class = getattr(module, configs['PromptClass'])

        return prompt_class(**configs['prompt_configs'])
    