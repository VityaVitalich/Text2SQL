from typing import Any, List, Union, Tuple


class SimplePrompt:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)

    def __call__(self, query: str, **kwargs: Any) -> str:
        return self._transforms(query)

    def _transforms(self, query: str) -> str:
        return self._insert_instructions(self._insert_few_shot(query))

    def _insert_few_shot(self, query: str) -> str:
        return self.few_shot_text + "\n" + query

    def _insert_instructions(self, query: str) -> str:
        return self.instruction_text + "\n" + query


class QuestionTableColumnsPrompt(SimplePrompt):
    def __call__(
        self,
        query: str,
        tables: Union[str, List[str]],
        columns: Union[str, List[str]],
        **kwargs: Any
    ) -> str:
        tables, columns = self.prepare(tables, columns)
        res = """question: {} {}: {}""".format(
            query, ", ".join(tables), ", ".join(columns)
        )

        return self._transforms(res)

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
