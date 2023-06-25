import importlib
from abc import ABC, abstractmethod
import openai
from openai import ChatCompletion
import yaml
from clickhouse_connect import get_client
from ratelimit import limits, sleep_and_retry
import signal
from contextlib import contextmanager
from typing import Dict, Any, TypeVar, Tuple, Iterator
from transformers import PreTrainedTokenizer, PreTrainedModel

T = TypeVar("T")


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds: int) -> Iterator[None]:
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class QueryInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """
        Initialization of model and all arguments
        """
        pass

    @abstractmethod
    def query(self) -> str:
        """
        query model with a question.
        extra arguments needed when using specific models
        """
        pass

    @abstractmethod
    def _init_model(self) -> None:
        """
        Model initialization, with a path of configs
        """

    @abstractmethod
    def _init_prompter(self) -> None:
        """
        Initialization of Prompt Changer class from config
        """


class DB_ClientMixin:
    def _init_db(self) -> None:
        with open(self.db_credentials_path, "r") as f:
            output = yaml.safe_load(f)

        self.client = get_client(**output)
        self.time_out = self.time_out if getattr(self, "time_out", None) else 10

    def execute_sql(self, sql_query: str) -> Any:
        with time_limit(self.time_out):
            return self.client.command(sql_query)

    def query_and_execute(self, question: str, **kwargs: Any) -> Any:
        if not getattr(self, "client", None):
            self._init_db()

        return self.execute_sql(self.query(question, **kwargs))


class HF_LLMQuery(QueryInterface, DB_ClientMixin):
    def __init__(
        self,
        model_config_path: str,
        prompt_config_path: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.model: PreTrainedModel
        self.tokenizer: PreTrainedTokenizer
        self.generation_args: Dict[str, Any]
        self.prompt_style: T
        self.__dict__.update(kwargs)
        self.model, self.tokenizer, self.generation_args = self._init_model(
            model_config_path
        )
        self.prompt_style = self._init_prompter(prompt_config_path)

    def query(self, question: str, **kwargs: Any) -> str:
        prompt = self.prompt_style(question, **kwargs)
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids

        output = self.model.generate(input_ids=input_ids, **self.generation_args)
        out_text = self.tokenizer.decode(output[0], skip_special_tokens=True)

        return out_text

    def _init_model(
        self, model_config_path: str
    ) -> Tuple[PreTrainedModel, PreTrainedTokenizer, Dict[str, Any]]:
        with open(f"{model_config_path}", "r") as f:
            configs = yaml.safe_load(f)

        module = importlib.import_module("transformers")

        TokenizerClass = module.__getattr__(configs["TokenizerClass"])
        ModelClass = module.__getattr__(configs["ModelClass"])

        tokenizer = TokenizerClass.from_pretrained(**configs["tokenizer"])
        model = ModelClass.from_pretrained(**configs["model"])

        return model, tokenizer, configs["generation_args"]

    def _init_prompter(self, prompt_config_path: str) -> T:
        with open(f"{prompt_config_path}", "r") as f:
            configs = yaml.safe_load(f)

        module = importlib.import_module("prompting.hf_prompt_schemas")

        prompt_class = getattr(module, configs["PromptClass"])

        return prompt_class(**configs["prompt_configs"])


class OpenAI_LLMQuery(QueryInterface, DB_ClientMixin):
    def __init__(
        self, model_config_path: str, prompt_config_path: str, *args: Any, **kwargs: Any
    ) -> None:
        self.model: ChatCompletion
        self.generation_args: Dict[str, Any]
        self.prompt_style: T
        self.__dict__.update(kwargs)
        self.model, self.generation_args = self._init_model(model_config_path)
        self.prompt_style = self._init_prompter(prompt_config_path)

    def query(self, question: str, **kwargs: Any) -> str:
        prompt = self.prompt_style(question, **kwargs)
        out_text = self.get_answer(prompt)

        return out_text

    def _init_model(
        self, model_config_path: str
    ) -> Tuple[ChatCompletion, Dict[str, Any]]:
        with open(f"{model_config_path}", "r") as f:
            configs = yaml.safe_load(f)

        openai.api_key = configs["token"]

        return openai.ChatCompletion, configs["generation_args"]

    def _init_prompter(self, prompt_config_path: str) -> T:
        with open(f"{prompt_config_path}", "r") as f:
            configs = yaml.safe_load(f)

        module = importlib.import_module("prompting.openai_prompt_schemas")

        prompt_class = getattr(module, configs["PromptClass"])

        return prompt_class(**configs["prompt_configs"])

    @sleep_and_retry
    @limits(calls=3, period=62)
    def get_answer(self, prompt: str) -> str:
        completion = self.model.create(messages=prompt, **self.generation_args)
        return str(completion["choices"][0]["message"]["content"])
