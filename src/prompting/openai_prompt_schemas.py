from typing import Any, Dict, List, Union, Tuple


class SimplePrompt:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)

    def __call__(self, query: str, **kwargs: Any) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": self.instruction_text},
            {"role": "user", "content": self.few_shot_text},
            {"role": "user", "content": query},
        ]


class QuestionTableColumnsPrompt(SimplePrompt):
    def __call__(
        self,
        query: str,
        tables: Union[str, List[str]],
        columns: Union[str, List[str]],
        **kwargs: Any
    ) -> List[Dict[str, str]]:
        tables, columns = self.prepare(tables, columns)
        res = """question: {} {}: {}""".format(
            query, ", ".join(tables), ", ".join(columns)
        )

        return [
            {"role": "system", "content": self.instruction_text},
            {"role": "user", "content": self.few_shot},
            {"role": "user", "content": res},
        ]

    def prepare(
        self, tables: Union[str, List[str]], columns: Union[str, List[str]]
    ) -> Tuple[List[str], List[str]]:
        if isinstance(tables, str):
            tables = [tables]
        if isinstance(columns, str):
            columns = [columns]

        assert isinstance(tables, list), "Passed tables are not List or Str"
        assert isinstance(columns, list), "Passed columns are not List or Str"

        return tables, columns
